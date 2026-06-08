"""Router Plants — Liên kết cây, Dashboard, Lịch sử, Cập nhật."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.admin import PlantTypeResponse
from app.schemas.plant import PlantPairRequest, PlantUpdateRequest
from app.services.admin_service import get_plant_types, provision_device
from app.services.plant_service import (
    get_dashboard,
    get_plant_history,
    pair_plant,
    update_plant,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/plants", tags=["Plants"])


@router.post("/diy-provision")
async def diy_provision_endpoint(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Tự cấp mã nạp mạch (Dành cho User tự cấu hình mạch ESP32)."""
    try:
        device_info = await provision_device(db)
        return {
            "status": "success",
            "message": "Đã tạo mã liên kết thiết bị thành công. Hãy nạp Plant Code vào ESP32.",
            "data": device_info,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/types", response_model=list[PlantTypeResponse])
async def get_all_plant_types(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[PlantTypeResponse]:
    """Lấy danh sách tất cả loại cây để hiển thị trên FE (select box)."""
    types = await get_plant_types(db)
    return [PlantTypeResponse.model_validate(t) for t in types]


@router.post("/pair")
async def pair_plant_endpoint(
    body: PlantPairRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Liên kết chậu cây với tài khoản (Secure Pairing).

    Cần: Plant Code + Verify Code (in trên thiết bị) + Tên cây + Loại cây.
    """
    try:
        plant = await pair_plant(
            db=db,
            user=user,
            plant_code=body.plant_code,
            verify_code=body.verify_code,
            name=body.name,
            plant_type_id=body.plant_type_id,
        )
        return {
            "status": "success",
            "message": f"Liên kết thành công! Cây '{plant.name}' bắt đầu tu luyện.",
            "plant_id": str(plant.id),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/me/dashboard")
async def get_dashboard_endpoint(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Lấy dữ liệu Dashboard: chỉ số, Tu Vi, Cảnh Giới, tiến trình."""
    try:
        return await get_dashboard(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/me/history")
async def get_history_endpoint(
    sensor_key: str = Query(
        ..., description="Loại cảm biến: soil_moisture, light, temperature, humidity"
    ),
    hours: int = Query(24, ge=1, le=168, description="Số giờ lịch sử (1-168)"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Lấy lịch sử cảm biến cho biểu đồ xu hướng."""
    valid_keys = {"soil_moisture", "light", "temperature", "humidity"}
    if sensor_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"sensor_key phải là một trong: {', '.join(valid_keys)}",
        )

    try:
        return await get_plant_history(db, user, sensor_key, hours)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put("/me")
async def update_plant_endpoint(
    body: PlantUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Cập nhật thông tin cây (tên, loại cây)."""
    try:
        plant = await update_plant(
            db=db,
            user=user,
            name=body.name,
            plant_type_id=body.plant_type_id,
        )
        return {
            "status": "success",
            "message": "Cập nhật thành công",
            "plant_name": plant.name,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
