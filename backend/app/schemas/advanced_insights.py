"""Schemas for advanced ML insights (PCMCI and STUMPY)."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class CausalLink(BaseModel):
    """Schema for a single causal relationship."""

    from_variable: str = Field(..., alias="from")
    to_variable: str = Field(..., alias="to")
    lag: int = Field(..., description="Time lag in days (0 = same day)")
    strength: float = Field(..., description="Correlation coefficient (-1 to 1)")
    p_value: float = Field(..., description="Statistical significance")
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    sample_size: Optional[int] = None

    class Config:
        populate_by_name = True


class CausalGraph(BaseModel):
    """Schema for causal graph structure."""

    nodes: List[Dict[str, str]]
    edges: List[Dict[str, Any]]


class CausalAnalysisResponse(BaseModel):
    """Schema for PCMCI causal analysis response."""

    method: str
    causal_links: List[CausalLink]
    causal_graph: Optional[CausalGraph] = None
    variables: List[str]
    tau_max: int
    alpha_level: float
    sample_size: int
    computed_at: Optional[str] = None


class PatternSummary(BaseModel):
    """Summary statistics for a pattern."""

    mean: float
    std: float
    min: float
    max: float
    duration_hours: Optional[int] = None


class RecurringPattern(BaseModel):
    """Schema for a recurring pattern (motif)."""

    pattern_id: int
    occurrences: int
    example_dates: List[str]
    example_times: Optional[List[str]] = None
    pattern_summary: PatternSummary
    pattern_values: Optional[List[float]] = None
    description: Optional[str] = None


class RecurringPatternsResponse(BaseModel):
    """Schema for recurring patterns response."""

    method: str
    window_size_hours: int
    patterns_found: int
    patterns: List[RecurringPattern]
    total_data_points: int


class Anomaly(BaseModel):
    """Schema for an anomalous pattern."""

    anomaly_id: int
    timestamp: str
    date: str
    time: str
    distance: Optional[float] = None
    z_score: Optional[float] = None
    severity: str = Field(..., pattern="^(high|medium|low)$")
    pattern_summary: Optional[PatternSummary] = None
    values: Optional[List[float]] = None
    description: Optional[str] = None


class AnomaliesResponse(BaseModel):
    """Schema for anomalies response."""

    method: str
    window_size_hours: Optional[int] = None
    anomalies_found: int
    anomalies: List[Anomaly]
    total_data_points: int


class SimilarDay(BaseModel):
    """Schema for a similar day."""

    date: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    mean_glucose: float
    std_glucose: float


class SimilarDaysResponse(BaseModel):
    """Schema for similar days response."""

    target_date: str
    similar_days_found: int
    top_similar_days: List[SimilarDay]


class TopCause(BaseModel):
    """Schema for top causes of a target variable."""

    cause: str
    lag_days: int
    strength: float
    p_value: float
    confidence: str
    interpretation: str


class TopCausesResponse(BaseModel):
    """Schema for top causes response."""

    target_variable: str
    top_causes: List[TopCause]
    explanation: str
