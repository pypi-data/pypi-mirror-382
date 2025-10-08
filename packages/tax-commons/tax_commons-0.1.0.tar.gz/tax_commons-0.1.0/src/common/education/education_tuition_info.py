from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator


# -------------------------------
# Core Tuition & Institution Info
# -------------------------------
class TuitionInfo(BaseModel):
    tuition_paid: Optional[confloat(ge=0)] = None # type: ignore
    education_institution: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    institution_type: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    program_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    field_of_study: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    education_level: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore

    @validator("tuition_paid")
    def validate_tuition(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 100_000:
                raise ValueError("tuition_paid exceeds maximum reasonable value")
        return v

    @validator("education_institution", always=True)
    def validate_institution_required(cls, v, values):
        tuition = values.get("tuition_paid")
        if tuition and tuition > 0 and not v:
            raise ValueError("education_institution is required if tuition_paid > 0")
        return v
    
    @validator("institution_type", "program_name", "field_of_study", "education_level", always=True)
    def validate_other_fields_required(cls, v, values):
        tuition = values.get("tuition_paid")
        if tuition and tuition > 0 and not v:
            raise ValueError(f"{v} is required if tuition_paid > 0")
        return v