"""HbA1c tracking model."""
from sqlalchemy import Column, BigInteger, Date, Integer, Numeric, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class HbA1c(Base):
    """HbA1c readings - tracks 3-month average glucose."""

    __tablename__ = "hba1c_readings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    test_date = Column(Date, nullable=False)
    hba1c_percent = Column(Numeric(3, 1), nullable=False)  # 6.5%
    hba1c_mmol_mol = Column(Integer)  # 48 mmol/mol (alternative unit)
    lab_name = Column(String(100))
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<HbA1c(user_id={self.user_id}, test_date={self.test_date}, value={self.hba1c_percent}%)>"
