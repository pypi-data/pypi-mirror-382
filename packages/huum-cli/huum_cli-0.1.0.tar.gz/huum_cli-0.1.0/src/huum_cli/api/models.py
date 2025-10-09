"""Pydantic models for Huum API entities."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SaunaDevice(BaseModel):
    """Represents a physical Huum sauna unit."""

    device_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    online: bool
    current_temperature: int = Field(..., ge=0, le=120)
    target_temperature: Optional[int] = Field(None, ge=40, le=110)
    heating_state: Literal["idle", "heating", "ready", "stopped"]
    session_active: bool
    last_updated: datetime


class AuthCredentials(BaseModel):
    """Represents authentication information for accessing the Huum API."""

    session: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    created_at: datetime


class Session(BaseModel):
    """Represents an active sauna heating session."""

    session_id: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    start_time: datetime
    end_time: Optional[datetime] = None
    target_temperature: int = Field(..., ge=40, le=110)
    state: Literal["active", "completed", "cancelled"]
    duration_minutes: Optional[int] = Field(None, ge=0, le=360)
