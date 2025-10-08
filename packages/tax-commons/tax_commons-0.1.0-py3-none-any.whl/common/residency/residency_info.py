from datetime import date
from email.headerregistry import Address
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, constr, field_validator, validator

from common.info.identification_info import IdentificationInfo
from common.residency.residency_duration import ResidencyDuration
from common.residency.residency_immigration_info import ImmigrationInfo
from common.tax_payer.enums.residency_status import ResidencyStatusType

# --- Aggregator ---
class ResidencyInfo(BaseModel):
    duration: ResidencyDuration
    immigration: ImmigrationInfo
    current_address: str  # use str instead of Address
    previous_address: Optional[str] = None
    identification: IdentificationInfo
    residency_status: Optional[ResidencyStatusType] = None
    months_in_canada: int = Field(default=12, ge=0, le=12)
    emigrated_this_year: bool = Field(default=False)
    emigration_date: Optional[date] = None
    immigrated_this_year: bool = Field(default=False)
    immigration_date: Optional[date] = None
    email: str

    # Convert email to Address internally if needed
    @field_validator("email", mode="before")
    def parse_email(cls, v):
        if isinstance(v, Address):
            return str(v.addr_spec)
        return v

    @validator("emigration_date", always=True)
    def validate_emigration(cls, v, values):
        if values.get("emigrated_this_year") and not v:
            raise ValueError("Emigration date required")
        return v

    @validator("immigration_date", always=True)
    def validate_immigration(cls, v, values):
        if values.get("immigrated_this_year") and not v:
            raise ValueError("Immigration date required")
        return v

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True  # <-- lets you still use Address in validators
