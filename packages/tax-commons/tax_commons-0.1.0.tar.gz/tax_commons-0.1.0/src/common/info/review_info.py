from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field, constr

class AggregatetInfo(BaseModel):
    total_dependents: int = 0
    total_children_under_18: int = 0
    total_children_18_to_25_in_school: int = 0
    total_other_dependents: int = 0
    total_disability_credits: int = 0
    total_medical_expenses: float = 0.0
    total_tuition_fees: float = 0.0
    total_student_loan_interest: float = 0.0
    total_child_care_expenses: float = 0.0
    total_eligible_dependents_amount: float = 0.0
    total_other_credits_amount: float = 0.0
    total_disability_credits_amount: float = 0.0
    total_medical_expenses_amount: float = 0.0
    total_tuition_fees_amount: float = 0.0
    total_student_loan_interest_amount: float = 0.0
    total_child_care_expenses_amount: float = 0.0
    total_credits_amount: float = 0.0
    total_deductions_amount: float = 0.0
    total_annual_income: float = 0.0
    created_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))