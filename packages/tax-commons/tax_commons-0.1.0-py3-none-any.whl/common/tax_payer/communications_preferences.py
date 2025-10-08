
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class CommunicationTracking(BaseModel):
    """Communication tracking"""
    preferred_contact_method: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    last_contact_date: Optional[datetime] = None
    last_contact_method: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    next_scheduled_contact: Optional[datetime] = None
    total_communications: int = Field(default=0, ge=0)

    @validator("total_communications")
    def validate_non_negative_counts(cls, v):
        if v < 0:
            raise ValueError("total_communications cannot be negative")
        return v