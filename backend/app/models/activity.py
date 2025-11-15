"""Activity/exercise model."""
from sqlalchemy import Column, BigInteger, String, Integer, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class Activity(Base):
    """Physical activity tracking."""

    __tablename__ = "activities"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    activity_type = Column(String(50))  # 'walking', 'running', 'cycling', 'strength'
    duration_minutes = Column(Integer)
    intensity = Column(String(20))  # 'light', 'moderate', 'vigorous'
    calories_burned = Column(Integer)
    heart_rate_avg = Column(Integer)
    source = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_activities_user_time", "user_id", "timestamp"),
    )

    def __repr__(self):
        return f"<Activity(user={self.user_id}, type={self.activity_type}, duration={self.duration_minutes}min)>"
