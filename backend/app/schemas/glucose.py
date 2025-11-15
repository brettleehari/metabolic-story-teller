"""Glucose reading schemas."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from uuid import UUID


class GlucoseReadingCreate(BaseModel):
    """Schema for creating a glucose reading."""

    timestamp: datetime
    value: float = Field(..., ge=20.0, le=600.0, description="Glucose value in mg/dL")
    source: Optional[str] = Field(None, max_length=50)
    device_id: Optional[str] = Field(None, max_length=100)


class GlucoseReadingResponse(BaseModel):
    """Schema for glucose reading response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    timestamp: datetime
    value: float
    source: Optional[str]
    device_id: Optional[str]
    created_at: datetime


class GlucoseBulkUpload(BaseModel):
    """Schema for bulk glucose upload."""

    readings: List[GlucoseReadingCreate] = Field(..., min_length=1, max_length=10000)
