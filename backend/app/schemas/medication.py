"""Medication schemas."""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class MedicationCreate(BaseModel):
    """Schema for creating medication."""
    medication_name: str = Field(..., max_length=100, description="Medication name")
    medication_type: Optional[str] = Field(
        None,
        pattern="^(insulin_basal|insulin_bolus|oral|other)$",
        description="Type of medication"
    )
    dosage: Optional[str] = Field(None, max_length=50, description="Dosage (e.g., '10 units', '500mg')")
    frequency: Optional[str] = Field(None, max_length=50, description="Frequency (e.g., 'daily', 'twice_daily')")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    is_active: bool = Field(True, description="Is medication currently active")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicationUpdate(BaseModel):
    """Schema for updating medication."""
    medication_name: Optional[str] = Field(None, max_length=100)
    medication_type: Optional[str] = Field(None, pattern="^(insulin_basal|insulin_bolus|oral|other)$")
    dosage: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class MedicationResponse(BaseModel):
    """Schema for medication response."""
    id: int
    user_id: str
    medication_name: str
    medication_type: Optional[str]
    dosage: Optional[str]
    frequency: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    is_active: bool
    notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
