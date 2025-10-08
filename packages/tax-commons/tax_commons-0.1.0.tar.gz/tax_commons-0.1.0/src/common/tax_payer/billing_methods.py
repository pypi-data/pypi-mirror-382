from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class BillingPayment(BaseModel):
    """Billing and payment information"""
    billing_method: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    payment_terms: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore
    credit_limit: Optional[float] = Field(default=None, ge=0)
    current_balance_due: Optional[float] = Field(default=0.0, ge=0)
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[float] = Field(default=None, ge=0)
    auto_pay_enabled: bool = Field(default=False)

    @validator("credit_limit", "current_balance_due", "last_payment_amount")
    def validate_financial_amounts(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Financial amounts cannot be negative")
            return round(v, 2)
        return v