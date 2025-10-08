from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

# -------------------------------
# Expenses
# -------------------------------
class ExpenseInfo(BaseModel):
    moving_expenses: confloat(ge=0) = Field(default=0.0) # type: ignore
    child_care_expenses: confloat(ge=0) = Field(default=0.0) # type: ignore
    employment_expenses: confloat(ge=0) = Field(default=0.0) # type: ignore

    @validator("*", pre=True)
    def validate_expenses(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 10_000_000:
                raise ValueError("Expense amount exceeds maximum reasonable value")
        return v
