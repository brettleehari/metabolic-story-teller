"""Sleep data schemas."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class SleepDataCreate(BaseModel):
    """Schema for creating sleep data."""

    date: date
    sleep_start: datetime
    sleep_end: datetime
    duration_minutes: Optional[int] = Field(None, ge=0, le=1440)
    deep_sleep_minutes: Optional[int] = Field(None, ge=0)
    rem_sleep_minutes: Optional[int] = Field(None, ge=0)
    light_sleep_minutes: Optional[int] = Field(None, ge=0)
    awake_minutes: Optional[int] = Field(None, ge=0)
    quality_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    source: Optional[str] = Field(None, max_length=50)


class SleepDataResponse(BaseModel):
    """Schema for sleep data response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    date: date
    sleep_start: datetime
    sleep_end: datetime
    duration_minutes: Optional[int]
    deep_sleep_minutes: Optional[int]
    rem_sleep_minutes: Optional[int]
    light_sleep_minutes: Optional[int]
    awake_minutes: Optional[int]
    quality_score: Optional[float]
    source: Optional[str]
    created_at: datetime
