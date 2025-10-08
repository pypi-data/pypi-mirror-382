from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class SpecialCircumstances(BaseModel):
    """Special circumstances and flags"""
    is_senior_citizen: bool = Field(default=False)
    is_first_time_filer: bool = Field(default=False)
    is_self_employed: bool = Field(default=False)
    has_business_number: bool = Field(default=False)
    business_number: Optional[constr(strip_whitespace=True, pattern=r'^\d{9}$')] = None # type: ignore
    has_rental_properties: bool = Field(default=False)
    has_foreign_income: bool = Field(default=False)
    has_foreign_assets: bool = Field(default=False)
    requires_special_attention: bool = Field(default=False)

    @validator("business_number", always=True)
    def validate_business_number(cls, v, values):
        has_bn = values.get("has_business_number")
        if has_bn and not v:
            raise ValueError("business_number is required when has_business_number is True")
        return v