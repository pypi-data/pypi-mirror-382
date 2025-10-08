from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, constr, validator

class ProvinceTerritory(str, Enum):
    """Canadian provinces and territories"""
    AB = "Alberta"
    BC = "British Columbia"
    MB = "Manitoba"
    NB = "New Brunswick"
    NL = "Newfoundland and Labrador"
    NS = "Nova Scotia"
    NT = "Northwest Territories"
    NU = "Nunavut"
    ON = "Ontario"
    PE = "Prince Edward Island"
    QC = "Quebec"
    SK = "Saskatchewan"
    YT = "Yukon"

class Address(BaseModel):
    street_address: constr(strip_whitespace=True, min_length=1, max_length=255) # type: ignore
    unit_number: Optional[constr(strip_whitespace=True, min_length=1, max_length=20)] = None # type: ignore
    city: constr(strip_whitespace=True, min_length=1, max_length=100) # type: ignore
    province_territory: ProvinceTerritory 
    postal_code: constr(strip_whitespace=True, pattern=r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$') # type: ignore
    country: constr(strip_whitespace=True, min_length=2, max_length=100) = "Canada" # type: ignore
    created_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("postal_code")
    def validate_postal_code(cls, v):
        clean_code = v.replace(" ", "").upper()
        if len(clean_code) != 6:
            raise ValueError("Postal code must be 6 characters")
        if not (clean_code[0].isalpha() and clean_code[1].isdigit() and 
                clean_code[2].isalpha() and clean_code[3].isdigit() and 
                clean_code[4].isalpha() and clean_code[5].isdigit()):
            raise ValueError("Postal code must follow format A1A 1A1")
        return f"{clean_code[:3]} {clean_code[3:]}"