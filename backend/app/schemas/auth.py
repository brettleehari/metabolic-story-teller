"""Authentication schemas."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    diabetes_type: Optional[str] = Field(None, pattern="^(type1|type2|prediabetes|gestational)$")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user response (without password)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: Optional[str]
    date_of_birth: Optional[datetime]
    diabetes_type: Optional[str]
    target_glucose_min: Optional[float]
    target_glucose_max: Optional[float]
    timezone: str
    created_at: datetime


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: Optional[str] = Field(None, max_length=255)
    date_of_birth: Optional[datetime] = None
    diabetes_type: Optional[str] = Field(None, pattern="^(type1|type2|prediabetes|gestational)$")
    target_glucose_min: Optional[float] = Field(None, ge=40.0, le=200.0)
    target_glucose_max: Optional[float] = Field(None, ge=40.0, le=400.0)
    timezone: Optional[str] = Field(None, max_length=50)


class PasswordChange(BaseModel):
    """Schema for changing password."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
