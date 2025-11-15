"""Meal schemas."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class MealCreate(BaseModel):
    """Schema for creating a meal."""

    timestamp: datetime
    meal_type: Optional[str] = Field(None, pattern="^(breakfast|lunch|dinner|snack)$")
    carbs_grams: Optional[float] = Field(None, ge=0)
    protein_grams: Optional[float] = Field(None, ge=0)
    fat_grams: Optional[float] = Field(None, ge=0)
    calories: Optional[int] = Field(None, ge=0)
    glycemic_load: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    source: Optional[str] = Field(None, max_length=50)


class MealResponse(BaseModel):
    """Schema for meal response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    timestamp: datetime
    meal_type: Optional[str]
    carbs_grams: Optional[float]
    protein_grams: Optional[float]
    fat_grams: Optional[float]
    calories: Optional[int]
    glycemic_load: Optional[float]
    description: Optional[str]
    photo_url: Optional[str]
    source: Optional[str]
    created_at: datetime
