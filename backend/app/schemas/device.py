"""Schemas Device — Request/Response cho quản lý thiết bị."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class DeviceCreateResponse(BaseModel):
    """Response khi Admin tạo thiết bị mới — trả về Plant Code + Verify Code gốc."""

    id: uuid.UUID
    plant_code: str
    verify_code: str  # Chỉ trả về 1 lần duy nhất khi tạo
    created_at: datetime


class DeviceListItem(BaseModel):
    """Một thiết bị trong danh sách quản lý."""

    id: uuid.UUID
    plant_code: str
    is_paired: bool
    is_active: bool
    last_seen_at: datetime | None
    paired_user_email: str | None
    paired_plant_name: str | None
    created_at: datetime


class DeviceResponse(BaseModel):
    """Thông tin thiết bị trả về."""

    id: uuid.UUID
    plant_code: str
    is_paired: bool
    is_active: bool
    last_seen_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceAuthRequest(BaseModel):
    """Request xác thực thiết bị."""

    verify_code: str


class DeviceAuthResponse(BaseModel):
    """Response sau khi thiết bị xác thực thành công."""

    access_token: str
    token_type: str = "bearer"
    created_at: datetime


class DeviceUpdateRequest(BaseModel):
    """Body cập nhật thiết bị (vô hiệu hóa/kích hoạt)."""

    is_active: bool
