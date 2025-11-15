"""Insights and analytics schemas."""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID


class CorrelationResponse(BaseModel):
    """Schema for correlation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    factor_x: str
    factor_y: str
    correlation_coefficient: float
    p_value: float
    lag_days: int
    sample_size: int
    confidence_level: str
    computed_at: datetime


class PatternResponse(BaseModel):
    """Schema for pattern response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pattern_type: str
    description: str
    confidence: Optional[float]
    support: Optional[float]
    occurrences: int
    example_dates: List[date]
    metadata: Optional[Dict[str, Any]]
    discovered_at: datetime


class DashboardSummary(BaseModel):
    """Schema for dashboard summary."""

    period_days: int
    avg_glucose: float
    time_in_range_percent: float
    avg_sleep_hours: Optional[float]
    total_exercise_minutes: Optional[int]
    top_correlations: List[CorrelationResponse]
    recent_patterns: List[PatternResponse]
