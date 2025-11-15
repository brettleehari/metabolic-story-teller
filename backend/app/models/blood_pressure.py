"""Blood pressure model (time-series)."""
from sqlalchemy import Column, BigInteger, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class BloodPressure(Base):
    """Blood pressure readings - time-series data."""

    __tablename__ = "blood_pressure"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    systolic = Column(Integer, nullable=False)  # 120 mmHg
    diastolic = Column(Integer, nullable=False)  # 80 mmHg
    heart_rate = Column(Integer)  # BPM
    source = Column(String(50))  # 'manual', 'blood_pressure_monitor', 'apple_health'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<BloodPressure(user_id={self.user_id}, bp={self.systolic}/{self.diastolic})>"
