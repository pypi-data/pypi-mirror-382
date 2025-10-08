from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, constr, validator


class ProvinceTerritory(str, Enum):
    ALBERTA = "Alberta"
    BRITISH_COLUMBIA = "British Columbia"
    MANITOBA = "Manitoba"
    NEW_BRUNSWICK = "New Brunswick"
    NEWFOUNDLAND_LABRADOR = "Newfoundland and Labrador"
    NORTHWEST_TERRITORIES = "Northwest Territories"
    NOVA_SCOTIA = "Nova Scotia"
    NUNAVUT = "Nunavut"
    ONTARIO = "Ontario"
    PRINCE_EDWARD_ISLAND = "Prince Edward Island"
    QUEBEC = "Quebec"
    SASKATCHEWAN = "Saskatchewan"
    YUKON = "Yukon"


# --- Identification Info ---
class IdentificationInfo(BaseModel):
    has_provincial_health_card: bool = Field(default=False)
    health_card_number: Optional[str] = None
    health_card_province: Optional[ProvinceTerritory] = None
    health_card_expiry_date: Optional[date] = None

    has_drivers_license: bool = Field(default=False)
    drivers_license_number: Optional[str] = None
    drivers_license_province: Optional[ProvinceTerritory] = None
    drivers_license_issue_date: Optional[date] = None
    drivers_license_expiry_date: Optional[date] = None

    eligible_for_spouse_amount: bool = Field(default=False)
    eligible_for_pension_splitting: bool = Field(default=False)
    eligible_for_disability_amount: bool = Field(default=False)
    eligible_for_caregiver_amount: bool = Field(default=False)
    eligible_for_medical_expenses: bool = Field(default=False)

    @validator("health_card_number", always=True)
    def validate_health_card_number(cls, v, values):
        if values.get("has_provincial_health_card") and not v:
            raise ValueError("Health card number required if has_provincial_health_card is True")
        return v

    @validator("drivers_license_number", always=True)
    def validate_license_number(cls, v, values):
        if values.get("has_drivers_license") and not v:
            raise ValueError("Driver's license number required if has_drivers_license is True")
        return v
