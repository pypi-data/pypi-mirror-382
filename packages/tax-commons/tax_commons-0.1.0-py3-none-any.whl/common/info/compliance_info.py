from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class ComplianceInfo(BaseModel):
    """Compliance and alerts"""
    compliance_score: Optional[int] = Field(default=100, ge=0, le=100)
    has_outstanding_obligations: bool = Field(default=False)
    has_penalties: bool = Field(default=False)
    has_interest_charges: bool = Field(default=False)
    has_payment_plan: bool = Field(default=False)
    payment_plan_active: bool = Field(default=False)

    @validator("compliance_score")
    def validate_compliance_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("compliance_score must be between 0 and 100")
        return v