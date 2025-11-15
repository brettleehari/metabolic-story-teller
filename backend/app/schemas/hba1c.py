"""HbA1c schemas."""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class HbA1cCreate(BaseModel):
    """Schema for creating HbA1c reading."""
    test_date: date = Field(..., description="Date of HbA1c test")
    hba1c_percent: float = Field(..., ge=3.0, le=20.0, description="HbA1c percentage (3-20%)")
    hba1c_mmol_mol: Optional[int] = Field(None, ge=9, le=200, description="HbA1c in mmol/mol (9-200)")
    lab_name: Optional[str] = Field(None, max_length=100, description="Laboratory name")
    notes: Optional[str] = Field(None, description="Additional notes")


class HbA1cResponse(BaseModel):
    """Schema for HbA1c reading response."""
    id: int
    user_id: str
    test_date: date
    hba1c_percent: float
    hba1c_mmol_mol: Optional[int]
    lab_name: Optional[str]
    notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True
