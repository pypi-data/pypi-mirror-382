from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, validator

from common.tax_payer.enums.bankrupcy_status import BankruptcyStatus

class BankruptcyInfo(BaseModel):
    bankruptcy_status: BankruptcyStatus = Field(default=BankruptcyStatus.NEVER_BANKRUPT)
    bankruptcy_filing_date: Optional[date] = None
    bankruptcy_discharge_date: Optional[date] = None

    @validator("bankruptcy_discharge_date", always=True)
    def validate_discharge(cls, v, values):
        filing = values.get("bankruptcy_filing_date")
        if values.get("bankruptcy_status") == BankruptcyStatus.DISCHARGED_BANKRUPT and not v:
            raise ValueError("Discharge date required")
        if v and filing and v < filing:
            raise ValueError("Discharge date cannot be before filing date")
        return v
