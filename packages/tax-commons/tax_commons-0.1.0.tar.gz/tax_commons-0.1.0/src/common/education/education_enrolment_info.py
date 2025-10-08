from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

# -------------------------------
# Enrollment & Study Period
# -------------------------------
class EnrollmentInfo(BaseModel):
    enrollment_status: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    student_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    study_period_start: Optional[date] = None
    study_period_end: Optional[date] = None
    months_in_study: Optional[int] = Field(default=None, ge=0, le=12)

    @validator("study_period_end", always=True)
    def validate_study_period(cls, v, values):
        start_date = values.get("study_period_start")
        if start_date and v and v < start_date:
            raise ValueError("study_period_end must be after study_period_start")
        return v

    @validator("months_in_study", always=True)
    def validate_months(cls, v, values):
        tuition = values.get("tuition_paid")
        enrollment = values.get("enrollment_status")
        if tuition and tuition > 0 and enrollment and (v is None or v == 0):
            raise ValueError("months_in_study is required when tuition is paid")
        return v
