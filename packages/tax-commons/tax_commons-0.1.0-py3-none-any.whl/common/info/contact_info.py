from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr, validator

class ContactInfo(BaseModel):
    email: EmailStr
    phone_number: constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$') # type: ignore
    alternate_phone: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None # type: ignore
    created_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("phone_number")
    def validate_phone_number(cls, v):
        clean_number = v.replace(" ", "").replace("-", "")
        if not (10 <= len(clean_number) <= 15) or not clean_number.lstrip('+').isdigit():
            raise ValueError("Phone number must be 10 to 15 digits, optionally starting with +")
        return clean_number
    
    @validator("alternate_phone")
    def validate_alternate_phone(cls, v):
        if v:
            clean_number = v.replace(" ", "").replace("-", "")
            if not (10 <= len(clean_number) <= 15) or not clean_number.lstrip('+').isdigit():
                raise ValueError("Alternate phone number must be 10 to 15 digits, optionally starting with +")
            return clean_number
        return v