from datetime import date
from typing import Optional
from pydantic import BaseModel, validator

from common.tax_payer.enums.immigration_status_type import ImmigrationStatusType

class ImmigrationInfo(BaseModel):
    immigration_status: Optional[ImmigrationStatusType] = None
    work_permit_expiry: Optional[date] = None
    study_permit_expiry: Optional[date] = None

    @validator("work_permit_expiry", always=True)
    def validate_work(cls, v, values):
        if values.get("immigration_status") == ImmigrationStatusType.WORK_PERMIT and not v:
            raise ValueError("Work permit expiry required")
        return v

    @validator("study_permit_expiry", always=True)
    def validate_study(cls, v, values):
        if values.get("immigration_status") == ImmigrationStatusType.STUDY_PERMIT and not v:
            raise ValueError("Study permit expiry required")
        return v
