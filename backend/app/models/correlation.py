"""Correlation analysis results model."""
from sqlalchemy import Column, BigInteger, String, Numeric, Integer, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class Correlation(Base):
    """Discovered correlations between factors."""

    __tablename__ = "correlations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    factor_x = Column(String(100))  # 'sleep_duration', 'exercise_minutes', 'carbs_intake'
    factor_y = Column(String(100))  # 'avg_glucose', 'glucose_variability'
    correlation_coefficient = Column(Numeric(4, 3))  # -1.00 to 1.00
    p_value = Column(Numeric(10, 8))
    lag_days = Column(Integer, default=0)  # e.g., sleep yesterday -> glucose today
    sample_size = Column(Integer)
    confidence_level = Column(String(10))  # 'high', 'medium', 'low'
    computed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "factor_x", "factor_y", "lag_days", name="uq_correlation"),
    )

    def __repr__(self):
        return f"<Correlation({self.factor_x} -> {self.factor_y}: r={self.correlation_coefficient}, lag={self.lag_days})>"
