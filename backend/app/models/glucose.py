"""Glucose reading model."""
from sqlalchemy import Column, BigInteger, String, Numeric, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime

from .base import Base


class GlucoseReading(Base):
    """Time-series glucose readings from CGM or manual entry."""

    __tablename__ = "glucose_readings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    value = Column(Numeric(5, 1), nullable=False)  # mg/dL (40.0 - 400.0)
    source = Column(String(50))  # 'cgm', 'manual', 'apple_health'
    device_id = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_glucose_user_time", "user_id", "timestamp"),
    )

    def __repr__(self):
        return f"<GlucoseReading(user={self.user_id}, value={self.value}, time={self.timestamp})>"
