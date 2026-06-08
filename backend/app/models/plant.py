"""Model Plant — Trung tâm hệ thống, liên kết User + Device, lưu Tu Vi & Cảnh Giới."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.breakthrough import BreakthroughEvent
    from app.models.config import PlantType, RankConfig
    from app.models.device import Device
    from app.models.exp_log import ExpLog
    from app.models.sensor_reading import SensorReading
    from app.models.user import User


class Plant(Base):
    """Bảng plants: mỗi bản ghi = 1 chậu cây được liên kết.

    - 1 User : 1 Plant (unique user_id)
    - 1 Device : 1 Plant (unique device_id)
    """

    __tablename__ = "plants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id"), unique=True, nullable=False
    )
    plant_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plant_types.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_exp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    current_rank_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rank_configs.id"), nullable=False
    )
    current_overall_quality: Mapped[str] = mapped_column(
        String(50), default="FAIR", nullable=False
    )
    last_exp_reward_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="plants")  # noqa: F821
    device: Mapped["Device"] = relationship(  # noqa: F821
        "Device", back_populates="plant"
    )
    plant_type: Mapped["PlantType"] = relationship("PlantType")  # noqa: F821
    current_rank: Mapped["RankConfig"] = relationship("RankConfig")  # noqa: F821
    sensor_readings: Mapped[list["SensorReading"]] = relationship(  # noqa: F821
        "SensorReading", back_populates="plant", order_by="SensorReading.created_at"
    )
    exp_logs: Mapped[list["ExpLog"]] = relationship(  # noqa: F821
        "ExpLog", back_populates="plant"
    )
    breakthroughs: Mapped[list["BreakthroughEvent"]] = relationship(  # noqa: F821
        "BreakthroughEvent", back_populates="plant"
    )
