from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, constr, validator


class ImmigrationStatus(str, Enum):
    CITIZEN = "Canadian Citizen"
    PERMANENT_RESIDENT = "Permanent Resident"
    WORK_PERMIT = "Work Permit"
    STUDY_PERMIT = "Study Permit"
    VISITOR = "Visitor"
    REFUGEE = "Refugee"
    OTHER = "Other"

# --- Immigration Info ---
class ImmigrationInfo(BaseModel):
    immigration_status: Optional[ImmigrationStatus] = None
    immigration_status_other: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None # type: ignore
    permanent_resident_card_number: Optional[str] = None
    work_permit_number: Optional[str] = None
    study_permit_number: Optional[str] = None
    date_became_permanent_resident: Optional[date] = None
    date_became_citizen: Optional[date] = None
    country_of_citizenship: Optional[str] = None

    @validator("immigration_status_other", always=True)
    def validate_immigration_other(cls, v, values):
        if values.get("immigration_status") == ImmigrationStatus.OTHER and not v:
            raise ValueError("immigration_status_other is required when immigration_status is 'Other'")
        return v

    @validator("permanent_resident_card_number", always=True)
    def validate_pr_card(cls, v, values):
        if values.get("immigration_status") == ImmigrationStatus.PERMANENT_RESIDENT and not v:
            raise ValueError("PR card number required for permanent residents")
        return v

    @validator("work_permit_number", always=True)
    def validate_work_permit(cls, v, values):
        if values.get("immigration_status") == ImmigrationStatus.WORK_PERMIT and not v:
            raise ValueError("work_permit_number is required for work permit holders")
        return v

    @validator("study_permit_number", always=True)
    def validate_study_permit(cls, v, values):
        if values.get("immigration_status") == ImmigrationStatus.STUDY_PERMIT and not v:
            raise ValueError("study_permit_number is required for study permit holders")
        return v