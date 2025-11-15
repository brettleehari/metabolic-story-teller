"""Daily aggregates model."""
from sqlalchemy import Column, BigInteger, Date, Numeric, Integer, TIMESTAMP, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class DailyAggregate(Base):
    """Pre-computed daily statistics for efficient querying."""

    __tablename__ = "daily_aggregates"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)

    # Glucose metrics
    avg_glucose = Column(Numeric(5, 1))
    min_glucose = Column(Numeric(5, 1))
    max_glucose = Column(Numeric(5, 1))
    std_glucose = Column(Numeric(5, 2))
    time_in_range_percent = Column(Numeric(5, 2))
    time_above_range_percent = Column(Numeric(5, 2))
    time_below_range_percent = Column(Numeric(5, 2))

    # Lifestyle metrics
    total_sleep_minutes = Column(Integer)
    sleep_quality_score = Column(Numeric(3, 1))
    total_exercise_minutes = Column(Integer)
    total_carbs_grams = Column(Numeric(7, 1))
    total_calories = Column(Integer)

    computed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_daily_agg_user_date", "user_id", "date"),
        UniqueConstraint("user_id", "date", name="uq_user_date"),
    )

    def __repr__(self):
        return f"<DailyAggregate(user={self.user_id}, date={self.date}, avg_glucose={self.avg_glucose})>"
