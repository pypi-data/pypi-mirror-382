from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class SecurityAccess(BaseModel):
    """Security and access control"""
    two_factor_enabled: bool = Field(default=False)
    security_questions_set: bool = Field(default=False)
    account_locked: bool = Field(default=False)
    failed_login_attempts: int = Field(default=0, ge=0)
    last_password_change: Optional[datetime] = None
    password_expiry_date: Optional[datetime] = None

    @validator("failed_login_attempts")
    def validate_non_negative_counts(cls, v):
        if v < 0:
            raise ValueError("failed_login_attempts cannot be negative")
        return v