from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

# -------------------------------
# Forms & Compliance
# -------------------------------
class EducationForms(BaseModel):
    t2202_form_available: bool = Field(default=False)
    t2202_form_number: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore
    international_student: bool = Field(default=False)
    study_permit_number: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore

    @validator("t2202_form_number", always=True)
    def validate_t2202(cls, v, values):
        if values.get("t2202_form_available") and not v:
            raise ValueError("t2202_form_number is required when T2202 form is available")
        return v

    @validator("study_permit_number", always=True)
    def validate_study_permit(cls, v, values):
        if values.get("international_student") and not v:
            raise ValueError("study_permit_number is required for international students")
        return v
