"""Blood pressure schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BloodPressureCreate(BaseModel):
    """Schema for creating blood pressure reading."""
    timestamp: datetime = Field(..., description="Timestamp of reading")
    systolic: int = Field(..., ge=50, le=250, description="Systolic pressure (50-250 mmHg)")
    diastolic: int = Field(..., ge=30, le=200, description="Diastolic pressure (30-200 mmHg)")
    heart_rate: Optional[int] = Field(None, ge=30, le=250, description="Heart rate (BPM)")
    source: Optional[str] = Field("manual", max_length=50, description="Data source")


class BloodPressureResponse(BaseModel):
    """Schema for blood pressure response."""
    id: int
    user_id: str
    timestamp: datetime
    systolic: int
    diastolic: int
    heart_rate: Optional[int]
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BloodPressureBulkUpload(BaseModel):
    """Schema for bulk uploading blood pressure readings."""
    readings: list[BloodPressureCreate] = Field(..., description="List of blood pressure readings")
