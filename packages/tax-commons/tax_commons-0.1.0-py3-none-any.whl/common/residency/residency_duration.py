from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, constr, validator


# --- Enums ---
class ResidencyStatus(str, Enum):
    CANADIAN_RESIDENT = "Canadian Resident"
    NON_RESIDENT = "Non-Resident"
    DEEMED_RESIDENT = "Deemed Resident"
    DEEMED_NON_RESIDENT = "Deemed Non-Resident"
    PART_YEAR_RESIDENT = "Part-Year Resident"
    EMIGRANT = "Emigrant"
    IMMIGRANT = "Immigrant"

# --- Residency Duration ---
class ResidencyDuration(BaseModel):
    canadian_resident: bool
    residency_status: Optional[ResidencyStatus] = None
    months_lived_in_canada: int = Field(ge=0, le=12)
    days_lived_in_canada: Optional[int] = Field(default=None, ge=0, le=366)

    is_part_year_resident: bool = Field(default=False)
    residency_start_date: Optional[date] = None
    residency_end_date: Optional[date] = None
    date_of_entry_to_canada: Optional[date] = None
    date_of_departure_from_canada: Optional[date] = None

    @validator("months_lived_in_canada")
    def validate_months(cls, v):
        if not (0 <= v <= 12):
            raise ValueError("months_lived_in_canada must be between 0 and 12")
        return v

    @validator("days_lived_in_canada")
    def validate_days(cls, v):
        if v is not None and not (0 <= v <= 366):
            raise ValueError("days_lived_in_canada must be between 0 and 366")
        return v

    @validator("residency_end_date", always=True)
    def validate_residency_dates(cls, v, values):
        start_date = values.get("residency_start_date")
        if start_date and v and v < start_date:
            raise ValueError("residency_end_date cannot be before residency_start_date")
        return v

    @validator("date_of_departure_from_canada", always=True)
    def validate_departure_date(cls, v, values):
        entry_date = values.get("date_of_entry_to_canada")
        if entry_date and v and v < entry_date:
            raise ValueError("date_of_departure_from_canada cannot be before entry date")
        return v
