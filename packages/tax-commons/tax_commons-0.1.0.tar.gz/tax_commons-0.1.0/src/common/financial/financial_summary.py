from typing import Optional
import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class FinancialSummary(BaseModel):
    """Financial summary information"""
    estimated_annual_income: Optional[float] = Field(default=None, ge=0)
    average_refund_amount: Optional[float] = Field(default=None, ge=0)
    total_lifetime_refunds: Optional[float] = Field(default=None, ge=0)
    total_lifetime_payments: Optional[float] = Field(default=None, ge=0)
    current_cra_balance: Optional[float] = Field(default=0.0)

    @validator("estimated_annual_income", "average_refund_amount", "total_lifetime_refunds",
               "total_lifetime_payments", "current_cra_balance")
    def validate_financial_amounts(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Financial amounts cannot be negative")
            return round(v, 2)
        return v