from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator


# -------------------------------
# Tax Credit Eligibility
# -------------------------------
class EducationCredits(BaseModel):
    eligible_for_education_credit: bool = Field(default=False)
    eligible_for_tuition_credit: bool = Field(default=False)
    eligible_for_student_loan_interest_credit: bool = Field(default=False)

    @validator("eligible_for_tuition_credit", always=True)
    def validate_tuition_credit(cls, v, values):
        tuition = values.get("tuition_paid")
        if v and (tuition is None or tuition == 0):
            raise ValueError("Cannot claim tuition credit without tuition paid")
        return v

    @validator("eligible_for_student_loan_interest_credit", always=True)
    def validate_interest_credit(cls, v, values):
        interest = values.get("student_loan_interest")
        if v and (interest is None or interest == 0):
            raise ValueError("Cannot claim student loan interest credit without interest paid")
        return v
