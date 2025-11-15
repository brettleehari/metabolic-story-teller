"""Insulin doses model (time-series)."""
from sqlalchemy import Column, BigInteger, Numeric, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class InsulinDose(Base):
    """Insulin dose records - time-series data."""

    __tablename__ = "insulin_doses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    insulin_type = Column(String(50), nullable=False)  # 'basal', 'bolus', 'correction'
    medication_name = Column(String(100))  # 'Humalog', 'Lantus', 'Novolog'
    dose_units = Column(Numeric(5, 2), nullable=False)  # 10.5 units
    carbs_grams = Column(Numeric(6, 1))  # For bolus doses (if insulin-to-carb ratio used)
    correction_target = Column(Numeric(5, 1))  # Target glucose for correction dose
    source = Column(String(50))  # 'manual', 'insulin_pump', 'apple_health'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<InsulinDose(user_id={self.user_id}, type={self.insulin_type}, dose={self.dose_units}u)>"
