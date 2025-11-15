"""Medications model."""
from sqlalchemy import Column, BigInteger, Boolean, Date, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class Medication(Base):
    """Medication and insulin prescriptions."""

    __tablename__ = "medications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    medication_name = Column(String(100), nullable=False)
    medication_type = Column(String(50))  # 'insulin_basal', 'insulin_bolus', 'oral', 'other'
    dosage = Column(String(50))  # '10 units', '500mg', etc.
    frequency = Column(String(50))  # 'daily', 'twice_daily', 'with_meals'
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Medication(user_id={self.user_id}, name={self.medication_name}, active={self.is_active})>"
