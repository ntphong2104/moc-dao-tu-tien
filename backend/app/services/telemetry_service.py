"""Telemetry Service — Xử lý dữ liệu cảm biến từ thiết bị IoT."""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.plant import Plant
from app.models.sensor_reading import SensorReading
from app.schemas.telemetry import SensorData
from app.services.exp_service import (
    classify_sensors_for_plant_type,
    get_overall_quality,
)
from app.services.sse_service import sse_manager

logger = logging.getLogger(__name__)

# Các sensor key hợp lệ
VALID_SENSOR_KEYS = {"soil_moisture", "light", "temperature", "humidity"}


async def process_telemetry(
    db: AsyncSession,
    plant_code: str,
    sensors: list[SensorData],
) -> dict:
    """Xử lý toàn bộ payload telemetry từ thiết bị.

    Flow:
    1. Tìm Device theo plant_code
    2. Kiểm tra Device đã paired & active
    3. Lấy Plant + PlantType
    4. Phân loại chất lượng từng sensor
    5. Lưu SensorReadings
    6. Tính Tu Vi (EXP)
    7. Broadcast SSE updates
    8. Cập nhật last_seen_at

    Returns:
        dict: Kết quả xử lý telemetry
    """
    # 1. Tìm Device
    stmt = select(Device).where(Device.plant_code == plant_code)
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if device is None:
        raise ValueError(f"Thiết bị không tồn tại: {plant_code}")

    if not device.is_active:
        raise ValueError(f"Thiết bị đã bị vô hiệu hóa: {plant_code}")

    if not device.is_paired:
        raise ValueError(f"Thiết bị chưa được liên kết: {plant_code}")

    # 2. Lấy Plant + PlantType
    stmt = (
        select(Plant)
        .where(Plant.device_id == device.id)
        .options(
            selectinload(Plant.plant_type),
            selectinload(Plant.current_rank),
        )
    )
    result = await db.execute(stmt)
    plant = result.scalar_one_or_none()

    if plant is None:
        raise ValueError(f"Không tìm thấy cây liên kết với thiết bị: {plant_code}")

    # 3. Validate & xây dựng sensor data
    sensor_data: dict[str, float] = {}
    for s in sensors:
        if s.key not in VALID_SENSOR_KEYS:
            logger.warning("Sensor key không hợp lệ: %s", s.key)
            continue
        sensor_data[s.key] = s.value

    if not sensor_data:
        raise ValueError("Không có dữ liệu cảm biến hợp lệ")

    # 4. Phân loại chất lượng
    qualities = classify_sensors_for_plant_type(sensor_data, plant.plant_type)
    overall_quality = get_overall_quality(list(qualities.values()))

    # 5. Lưu SensorReadings
    for key, value in sensor_data.items():
        reading = SensorReading(
            plant_id=plant.id,
            sensor_key=key,
            value=value,
            quality=qualities.get(key, "FAIR"),
        )
        db.add(reading)

    # 6. Cập nhật last_seen_at và current_overall_quality
    device.last_seen_at = datetime.now(UTC)
    plant.current_overall_quality = overall_quality

    # 8. Broadcast sensor update qua SSE
    await sse_manager.broadcast(
        plant.id,
        "sensor_update",
        {
            "sensors": {
                k: {"value": v, "quality": qualities.get(k, "FAIR")}
                for k, v in sensor_data.items()
            },
            "overall_quality": overall_quality,
            "device_last_seen": datetime.now(UTC).isoformat(),
        },
    )

    await db.flush()

    return {
        "status": "ok",
        "message": f"Xử lý thành công. Chất lượng: {overall_quality}",
    }
