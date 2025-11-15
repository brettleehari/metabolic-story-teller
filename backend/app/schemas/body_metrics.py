"""Body metrics schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BodyMetricsCreate(BaseModel):
    """Schema for creating body metrics."""
    timestamp: datetime = Field(..., description="Timestamp of measurement")
    weight_kg: Optional[float] = Field(None, ge=20.0, le=300.0, description="Weight in kg (20-300)")
    body_fat_percent: Optional[float] = Field(None, ge=3.0, le=70.0, description="Body fat percentage (3-70%)")
    muscle_mass_kg: Optional[float] = Field(None, ge=10.0, le=150.0, description="Muscle mass in kg")
    waist_cm: Optional[float] = Field(None, ge=40.0, le=200.0, description="Waist circumference in cm")
    bmi: Optional[float] = Field(None, ge=10.0, le=60.0, description="BMI (auto-calculated or manual)")
    source: Optional[str] = Field("manual", max_length=50, description="Data source")


class BodyMetricsResponse(BaseModel):
    """Schema for body metrics response."""
    id: int
    user_id: str
    timestamp: datetime
    weight_kg: Optional[float]
    body_fat_percent: Optional[float]
    muscle_mass_kg: Optional[float]
    waist_cm: Optional[float]
    bmi: Optional[float]
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BodyMetricsBulkUpload(BaseModel):
    """Schema for bulk uploading body metrics."""
    metrics: list[BodyMetricsCreate] = Field(..., description="List of body metrics")
