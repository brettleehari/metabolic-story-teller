"""Discovered patterns model."""
from sqlalchemy import Column, BigInteger, String, Numeric, Integer, TIMESTAMP, Text, ARRAY, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from .base import Base


class Pattern(Base):
    """Discovered patterns and insights."""

    __tablename__ = "patterns"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    pattern_type = Column(String(50))  # 'recurring', 'anomaly', 'association_rule'
    description = Column(Text)
    confidence = Column(Numeric(5, 4))  # 0-1 for association rules
    support = Column(Numeric(5, 4))
    occurrences = Column(Integer)
    example_dates = Column(ARRAY(Date))
    metadata = Column(JSONB)  # flexible storage for pattern details
    discovered_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Pattern(type={self.pattern_type}, confidence={self.confidence}, occurrences={self.occurrences})>"
