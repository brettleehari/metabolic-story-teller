"""Meal tracking model."""
from sqlalchemy import Column, BigInteger, String, Integer, Numeric, TIMESTAMP, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class Meal(Base):
    """Meal and nutrition tracking."""

    __tablename__ = "meals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    meal_type = Column(String(20))  # 'breakfast', 'lunch', 'dinner', 'snack'
    carbs_grams = Column(Numeric(6, 1))
    protein_grams = Column(Numeric(6, 1))
    fat_grams = Column(Numeric(6, 1))
    calories = Column(Integer)
    glycemic_load = Column(Numeric(4, 1))
    description = Column(Text)
    photo_url = Column(String(500))
    source = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_meals_user_time", "user_id", "timestamp"),
    )

    def __repr__(self):
        return f"<Meal(user={self.user_id}, type={self.meal_type}, carbs={self.carbs_grams}g)>"
