"""User model."""
from sqlalchemy import Column, String, Date, Numeric, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .base import Base


class User(Base):
    """User account information."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    date_of_birth = Column(Date)

    # Biometric data
    height_cm = Column(Numeric(5, 2))  # 150.5 cm
    weight_kg = Column(Numeric(5, 2))  # 70.5 kg
    gender = Column(String(20))  # 'male', 'female', 'other', 'prefer_not_to_say'

    # Diabetes management
    diabetes_type = Column(String(20))  # 'type1', 'type2', 'prediabetes', 'gestational'
    diagnosis_date = Column(Date)
    insulin_dependent = Column(Boolean, default=False)
    ethnicity = Column(String(50))  # Risk factor for diabetes
    cgm_type = Column(String(50))  # 'dexcom_g7', 'freestyle_libre', etc.

    # Target ranges
    target_glucose_min = Column(Numeric(5, 1), default=70.0)
    target_glucose_max = Column(Numeric(5, 1), default=180.0)

    # System settings
    timezone = Column(String(50), default="UTC")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(email={self.email}, name={self.full_name})>"
