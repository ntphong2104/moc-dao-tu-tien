"""Schemas Telemetry — Dữ liệu cảm biến từ thiết bị IoT."""

from pydantic import BaseModel


class SensorData(BaseModel):
    """Một chỉ số cảm biến."""

    key: str  # "soil_moisture" | "light" | "temperature" | "humidity"
    value: float


class TelemetryPayload(BaseModel):
    """Payload telemetry từ thiết bị.

    Thiết bị gửi danh sách các cảm biến mỗi chu kỳ (60s).
    Yêu cầu phải có token xác thực.
    """

    token: str
    sensors: list[SensorData]


class TelemetryResponse(BaseModel):
    """Response xác nhận đã nhận telemetry."""

    status: str = "ok"
    exp_awarded: bool
    message: str | None = None
