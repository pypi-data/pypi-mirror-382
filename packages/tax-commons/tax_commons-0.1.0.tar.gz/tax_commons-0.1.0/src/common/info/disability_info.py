# --- Submodels ---
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, validator

from common.tax_payer.enums.disability_status import DisabilityStatus

class DisabilityInfo(BaseModel):
    disability_status: DisabilityStatus = Field(default=DisabilityStatus.NONE)
    disability_certificate_number: Optional[str] = None
    disability_approval_date: Optional[date] = None
    disability_start_date: Optional[date] = None
    disability_end_date: Optional[date] = None
    disability_percentage: Optional[int] = Field(default=None, ge=0, le=100)

    @validator("disability_certificate_number", always=True)
    def validate_certificate(cls, v, values):
        if values.get("disability_status") == DisabilityStatus.APPROVED_DTC and not v:
            raise ValueError("Certificate number required for Approved DTC")
        return v

    @validator("disability_approval_date", always=True)
    def validate_approval_date(cls, v, values):
        if values.get("disability_status") == DisabilityStatus.APPROVED_DTC and not v:
            raise ValueError("Approval date required for Approved DTC")
        return v

    @validator("disability_end_date", always=True)
    def validate_dates(cls, v, values):
        start = values.get("disability_start_date")
        if start and v and v < start:
            raise ValueError("End date cannot be before start date")
        return v
