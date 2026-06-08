"""Router Devices — Telemetry endpoint cho thiết bị IoT."""

import logging

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.device import Device
from app.schemas.device import DeviceAuthRequest, DeviceAuthResponse
from app.schemas.telemetry import TelemetryPayload, TelemetryResponse
from app.services.auth_service import create_device_token, decode_token
from app.services.telemetry_service import process_telemetry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/devices", tags=["Devices"])


@router.post("/{plant_code}/auth", response_model=DeviceAuthResponse)
async def authenticate_device(
    plant_code: str,
    body: DeviceAuthRequest,
    db: AsyncSession = Depends(get_db),
) -> DeviceAuthResponse:
    """Xác thực thiết bị IoT lần đầu bằng verify_code để lấy Token."""
    stmt = select(Device).where(Device.plant_code == plant_code)
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thiết bị",
        )

    # Kiểm tra mã verify_code bằng bcrypt
    if not bcrypt.checkpw(
        body.verify_code.encode("utf-8"),
        device.verify_hash.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã xác thực không hợp lệ",
        )

    from datetime import datetime, UTC

    token = create_device_token(plant_code)
    return DeviceAuthResponse(
        access_token=token,
        token_type="bearer",
        created_at=datetime.now(UTC),
    )


@router.post("/{plant_code}/telemetry", response_model=TelemetryResponse)
async def receive_telemetry(
    plant_code: str,
    body: TelemetryPayload,
    db: AsyncSession = Depends(get_db),
) -> TelemetryResponse:
    """Nhận dữ liệu cảm biến từ thiết bị IoT (REST fallback).

    Auth: Bắt buộc phải có token JWT hợp lệ của chính thiết bị đó trong payload.
    """
    # Xác thực JWT Token
    try:
        token_data = decode_token(body.token)
        if token_data.get("type") != "device" or token_data.get("sub") != plant_code:
            raise ValueError("Token không thuộc về thiết bị này")
    except ValueError as e:
        logger.warning("Lỗi xác thực Telemetry (HTTP) cho %s: %s", plant_code, e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
        ) from e

    try:
        result = await process_telemetry(db, plant_code, body.sensors)
        return TelemetryResponse(
            status=result["status"],
            exp_awarded=result["exp_awarded"],
            message=result.get("message"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
