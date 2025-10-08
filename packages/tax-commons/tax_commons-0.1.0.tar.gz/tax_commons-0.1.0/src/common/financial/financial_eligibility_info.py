from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

# -------------------------------
# Tax Eligibility
# -------------------------------
class EligibilityInfo(BaseModel):
    eligible_for_canada_caregiver_amount: bool = Field(default=False)
    eligible_for_disability_amount: bool = Field(default=False)

    @validator("eligible_for_disability_amount")
    def validate_disability(cls, v, values):
        if v and values.get("net_income") is None:
            raise ValueError("Cannot claim disability amount without net income")
        return v
