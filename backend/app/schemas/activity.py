"""Activity schemas."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class ActivityCreate(BaseModel):
    """Schema for creating an activity."""

    timestamp: datetime
    activity_type: Optional[str] = Field(None, max_length=50)
    duration_minutes: Optional[int] = Field(None, ge=0)
    intensity: Optional[str] = Field(None, pattern="^(light|moderate|vigorous)$")
    calories_burned: Optional[int] = Field(None, ge=0)
    heart_rate_avg: Optional[int] = Field(None, ge=30, le=250)
    source: Optional[str] = Field(None, max_length=50)


class ActivityResponse(BaseModel):
    """Schema for activity response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    timestamp: datetime
    activity_type: Optional[str]
    duration_minutes: Optional[int]
    intensity: Optional[str]
    calories_burned: Optional[int]
    heart_rate_avg: Optional[int]
    source: Optional[str]
    created_at: datetime
