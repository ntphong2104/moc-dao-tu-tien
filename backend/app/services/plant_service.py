"""Plant Service — Liên kết chậu cây & quản lý hồ sơ cây."""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.config import PlantType, RankConfig
from app.models.device import Device
from app.models.plant import Plant
from app.models.sensor_reading import SensorReading
from app.models.user import User
from app.services.exp_service import (
    get_next_rank,
    get_overall_quality,
)

logger = logging.getLogger(__name__)

# Thời gian để coi thiết bị là offline (giây)
DEVICE_OFFLINE_THRESHOLD = 120


async def pair_plant(
    db: AsyncSession,
    user: User,
    plant_code: str,
    verify_code: str,
    name: str,
    plant_type_id: UUID,
) -> Plant:
    """Liên kết chậu cây với tài khoản người dùng (Secure Pairing).

    Flow:
    1. Kiểm tra user chưa có cây
    2. Tìm device theo plant_code
    3. Xác thực verify_code (bcrypt)
    4. Kiểm tra device chưa paired
    5. Kiểm tra plant_type tồn tại
    6. Lấy Cảnh Giới mặc định (Phàm Mộc)
    7. Tạo Plant record

    Raises:
        ValueError: Khi xác thực thất bại hoặc vi phạm ràng buộc.
    """
    # 1. Bỏ giới hạn 1 user - 1 cây để hỗ trợ Đa chậu
    # stmt = select(Plant).where(Plant.user_id == user.id)

    # 2. Tìm device
    stmt = select(Device).where(Device.plant_code == plant_code)
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if device is None:
        raise ValueError("Plant Code không hợp lệ")

    if not device.is_active:
        raise ValueError("Thiết bị đã bị vô hiệu hóa")

    if device.is_paired:
        raise ValueError("Thiết bị đã được liên kết với tài khoản khác")

    # 3. Xác thực verify_code
    if not bcrypt.checkpw(
        verify_code.encode("utf-8"),
        device.verify_hash.encode("utf-8"),
    ):
        raise ValueError("Verify Code không chính xác")

    # 4. Kiểm tra plant_type
    stmt = select(PlantType).where(PlantType.id == plant_type_id)
    result = await db.execute(stmt)
    plant_type = result.scalar_one_or_none()
    if plant_type is None:
        raise ValueError("Loại cây không tồn tại")

    # 5. Lấy rank mặc định (order = 1 → Phàm Mộc)
    stmt = select(RankConfig).order_by(RankConfig.order.asc()).limit(1)
    result = await db.execute(stmt)
    default_rank = result.scalar_one_or_none()
    if default_rank is None:
        raise ValueError("Chưa có cấu hình Cảnh Giới. Admin cần tạo trước.")

    # 6. Tạo Plant
    plant = Plant(
        user_id=user.id,
        device_id=device.id,
        plant_type_id=plant_type_id,
        name=name,
        total_exp=0.0,
        current_rank_id=default_rank.id,
    )
    db.add(plant)

    # Đánh dấu device đã paired
    device.is_paired = True

    await db.flush()
    logger.info(
        "🌱 Liên kết thành công: User '%s' ← Device '%s' → Cây '%s' (%s)",
        user.email,
        plant_code,
        name,
        plant_type.name,
    )

    return plant


async def get_dashboard(db: AsyncSession, user: User) -> dict:
    """Lấy dữ liệu Dashboard cho người dùng.

    Returns:
        dict chứa: plant info, sensors, EXP, rank, progress, device status.
    """
    # Lấy plant với relationships
    stmt = (
        select(Plant)
        .where(Plant.user_id == user.id)
        .options(
            selectinload(Plant.plant_type),
            selectinload(Plant.current_rank),
            selectinload(Plant.device),
        )
    )
    result = await db.execute(stmt)
    plant = result.scalar_one_or_none()

    if plant is None:
        raise ValueError("Chưa liên kết chậu cây")

    # Lấy sensor readings mới nhất (1 bản ghi cho mỗi sensor_key)
    sensors = []
    for key in ["soil_moisture", "light", "temperature", "humidity"]:
        stmt = (
            select(SensorReading)
            .where(
                SensorReading.plant_id == plant.id,
                SensorReading.sensor_key == key,
            )
            .order_by(SensorReading.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        reading = result.scalar_one_or_none()
        if reading:
            sensors.append(
                {
                    "sensor_key": key,
                    "value": reading.value,
                    "quality": reading.quality,
                    "updated_at": reading.created_at.isoformat(),
                }
            )

    # Tính overall quality từ sensors hiện tại
    qualities = [s["quality"] for s in sensors]
    overall_quality = get_overall_quality(qualities)

    # Lấy next rank
    next_rank_data = None
    exp_to_next = None
    next_rank = await get_next_rank(db, plant.current_rank.order)
    if next_rank:
        next_rank_data = {
            "id": str(next_rank.id),
            "order": next_rank.order,
            "name": next_rank.name,
            "min_exp": next_rank.min_exp,
        }
        exp_to_next = max(0, next_rank.min_exp - plant.total_exp)

    # Kiểm tra device online
    device_online = False
    if plant.device.last_seen_at:
        now = datetime.now(UTC)
        last_seen = plant.device.last_seen_at
        if last_seen.tzinfo is None:
            from datetime import timezone

            last_seen = last_seen.replace(tzinfo=timezone.utc)
        device_online = (now - last_seen).total_seconds() < DEVICE_OFFLINE_THRESHOLD

    return {
        "plant_id": str(plant.id),
        "plant_name": plant.name,
        "plant_type": {
            "id": str(plant.plant_type.id),
            "name": plant.plant_type.name,
        },
        "total_exp": plant.total_exp,
        "current_rank": {
            "id": str(plant.current_rank.id),
            "order": plant.current_rank.order,
            "name": plant.current_rank.name,
            "min_exp": plant.current_rank.min_exp,
        },
        "next_rank": next_rank_data,
        "exp_to_next_rank": exp_to_next,
        "sensors": sensors,
        "overall_quality": overall_quality,
        "device_online": device_online,
        "device_last_seen": plant.device.last_seen_at.isoformat()
        if plant.device.last_seen_at
        else None,
    }


async def get_plant_history(
    db: AsyncSession,
    user: User,
    sensor_key: str,
    hours: int = 24,
) -> dict:
    """Lấy lịch sử cảm biến cho biểu đồ xu hướng.

    Args:
        sensor_key: "soil_moisture" | "light" | "temperature" | "humidity"
        hours: Số giờ lịch sử (mặc định 24h)

    Returns:
        dict chứa readings và ngưỡng lý tưởng.
    """
    # Lấy plant
    stmt = (
        select(Plant)
        .where(Plant.user_id == user.id)
        .options(selectinload(Plant.plant_type))
    )
    result = await db.execute(stmt)
    plant = result.scalar_one_or_none()

    if plant is None:
        raise ValueError("Chưa liên kết chậu cây")

    # Query readings trong khoảng thời gian
    since = datetime.now(UTC) - timedelta(hours=hours)
    stmt = (
        select(SensorReading)
        .where(
            SensorReading.plant_id == plant.id,
            SensorReading.sensor_key == sensor_key,
            SensorReading.created_at >= since,
        )
        .order_by(SensorReading.created_at.asc())
    )
    result = await db.execute(stmt)
    readings = result.scalars().all()

    # Lấy ngưỡng lý tưởng
    thresholds = {
        "soil_moisture": (
            plant.plant_type.soil_moisture_min,
            plant.plant_type.soil_moisture_max,
        ),
        "light": (plant.plant_type.light_min, plant.plant_type.light_max),
        "temperature": (
            plant.plant_type.temperature_min,
            plant.plant_type.temperature_max,
        ),
        "humidity": (plant.plant_type.humidity_min, plant.plant_type.humidity_max),
    }
    ideal_min, ideal_max = thresholds.get(sensor_key, (0, 100))

    return {
        "sensor_key": sensor_key,
        "readings": [
            {
                "value": r.value,
                "quality": r.quality,
                "created_at": r.created_at.isoformat(),
            }
            for r in readings
        ],
        "ideal_min": ideal_min,
        "ideal_max": ideal_max,
    }


async def update_plant(
    db: AsyncSession,
    user: User,
    name: str | None = None,
    plant_type_id: UUID | None = None,
) -> Plant:
    """Cập nhật thông tin cây (tên, loại cây)."""
    stmt = (
        select(Plant)
        .where(Plant.user_id == user.id)
        .options(
            selectinload(Plant.plant_type),
            selectinload(Plant.current_rank),
        )
    )
    result = await db.execute(stmt)
    plant = result.scalar_one_or_none()

    if plant is None:
        raise ValueError("Chưa liên kết chậu cây")

    if name is not None:
        plant.name = name

    if plant_type_id is not None:
        # Kiểm tra plant_type tồn tại
        stmt = select(PlantType).where(PlantType.id == plant_type_id)
        result = await db.execute(stmt)
        plant_type = result.scalar_one_or_none()
        if plant_type is None:
            raise ValueError("Loại cây không tồn tại")
        plant.plant_type_id = plant_type_id

    await db.flush()
    return plant
