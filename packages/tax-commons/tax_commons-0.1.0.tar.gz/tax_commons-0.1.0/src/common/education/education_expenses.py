from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator


# -------------------------------
# Expenses & Financial Aid
# -------------------------------
class EducationExpenses(BaseModel):
    textbooks_expenses: Optional[confloat(ge=0)] = None # type: ignore
    mandatory_fees: Optional[confloat(ge=0)] = None # type: ignore
    student_loan_interest: Optional[confloat(ge=0)] = None # type: ignore

    scholarships_received: Optional[confloat(ge=0)] = None # type: ignore
    bursaries_received: Optional[confloat(ge=0)] = None # type: ignore
    grants_received: Optional[confloat(ge=0)] = None # type: ignore

    transferred_tuition_amount: Optional[confloat(ge=0)] = None # type: ignore
    carried_forward_tuition_amount: Optional[confloat(ge=0)] = None # type: ignore

    @validator("*", pre=True)
    def validate_amounts(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 100_000:
                raise ValueError("Education-related amount exceeds maximum reasonable value")
        return v
