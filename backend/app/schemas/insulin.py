"""Insulin dose schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class InsulinDoseCreate(BaseModel):
    """Schema for creating insulin dose."""
    timestamp: datetime = Field(..., description="Timestamp of insulin dose")
    insulin_type: str = Field(
        ...,
        pattern="^(basal|bolus|correction)$",
        description="Type of insulin dose"
    )
    medication_name: Optional[str] = Field(None, max_length=100, description="Insulin brand (e.g., 'Humalog')")
    dose_units: float = Field(..., ge=0.1, le=100.0, description="Dose in units (0.1-100)")
    carbs_grams: Optional[float] = Field(None, ge=0, le=500, description="Carbs for bolus dose")
    correction_target: Optional[float] = Field(None, ge=50, le=200, description="Target glucose for correction")
    source: Optional[str] = Field("manual", max_length=50, description="Data source")


class InsulinDoseResponse(BaseModel):
    """Schema for insulin dose response."""
    id: int
    user_id: str
    timestamp: datetime
    insulin_type: str
    medication_name: Optional[str]
    dose_units: float
    carbs_grams: Optional[float]
    correction_target: Optional[float]
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InsulinDoseBulkUpload(BaseModel):
    """Schema for bulk uploading insulin doses."""
    doses: list[InsulinDoseCreate] = Field(..., description="List of insulin doses")
