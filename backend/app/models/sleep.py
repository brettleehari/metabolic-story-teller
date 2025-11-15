"""Sleep data model."""
from sqlalchemy import Column, BigInteger, String, Integer, Numeric, TIMESTAMP, Date, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class SleepData(Base):
    """Sleep session tracking."""

    __tablename__ = "sleep_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    sleep_start = Column(TIMESTAMP(timezone=True), nullable=False)
    sleep_end = Column(TIMESTAMP(timezone=True), nullable=False)
    duration_minutes = Column(Integer)  # total sleep
    deep_sleep_minutes = Column(Integer)
    rem_sleep_minutes = Column(Integer)
    light_sleep_minutes = Column(Integer)
    awake_minutes = Column(Integer)
    quality_score = Column(Numeric(3, 1))  # 0-10 scale
    source = Column(String(50))  # 'apple_health', 'fitbit', 'oura', 'manual'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_sleep_user_date", "user_id", "date"),
    )

    def __repr__(self):
        return f"<SleepData(user={self.user_id}, date={self.date}, duration={self.duration_minutes}min)>"
