"""Body metrics model (time-series)."""
from sqlalchemy import Column, BigInteger, Numeric, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class BodyMetrics(Base):
    """Body metrics timeline - track weight, body composition, etc."""

    __tablename__ = "body_metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    weight_kg = Column(Numeric(5, 2))  # 70.5 kg
    body_fat_percent = Column(Numeric(4, 1))  # 22.5%
    muscle_mass_kg = Column(Numeric(5, 2))  # 50.0 kg
    waist_cm = Column(Numeric(5, 1))  # 85.0 cm
    bmi = Column(Numeric(4, 1))  # Auto-calculated
    source = Column(String(50))  # 'manual', 'smart_scale', 'apple_health'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<BodyMetrics(user_id={self.user_id}, weight={self.weight_kg}kg, bmi={self.bmi})>"
