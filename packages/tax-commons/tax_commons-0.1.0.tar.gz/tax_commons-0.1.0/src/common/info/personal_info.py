from datetime import date, datetime, timezone
from typing import Any, Dict, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator


def serialize_personal_info(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB personal info document into JSON-serializable dict.
    Handles ObjectId, datetime, and renames _id to id.
    """
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return jsonable_encoder(doc)


class PersonalInfo(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1, max_length=100)  # type: ignore
    middle_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    last_name: constr(strip_whitespace=True, min_length=1, max_length=100)  # type: ignore
    preferred_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    suffix: Optional[constr(strip_whitespace=True, min_length=1, max_length=20)] = None  # type: ignore  # Jr., Sr., III, etc.
    date_of_birth: date
    gender: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    email: Optional[EmailStr] = None
    phone_primary: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None  # type: ignore
    phone_secondary: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None  # type: ignore
    street_address: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None  # type: ignore
    apartment_unit: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    city: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    province_state: Optional[constr(strip_whitespace=True, min_length=2, max_length=100)] = None  # type: ignore
    postal_code: Optional[constr(strip_whitespace=True, pattern=r'^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$')] = None  # type: ignore
    country: constr(strip_whitespace=True, min_length=1, max_length=100) = Field(default="Canada")  # type: ignore
    citizenship_status: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    passport_number: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    drivers_license_number: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    drivers_license_province: Optional[constr(strip_whitespace=True, min_length=2, max_length=50)] = None  # type: ignore
    primary_language: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = Field(default="English")  # type: ignore
    secondary_language: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    preferred_contact_method: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    emergency_contact_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None  # type: ignore
    emergency_contact_phone: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None  # type: ignore
    emergency_contact_relationship: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    marital_status: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    occupation: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None  # type: ignore
    employer_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None  # type: ignore
    personal_notes: Optional[constr(strip_whitespace=True, max_length=1000)] = None  # type: ignore
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ---------------- Validators ---------------- #

    @validator("first_name", "last_name")
    def validate_name_fields(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty or only whitespace")
        if len(v.strip()) < 2:
            raise ValueError("Name must contain at least 2 characters")
        if not all(c.isalpha() or c.isspace() or c in "-'" for c in v):
            raise ValueError("Name must contain only letters, spaces, hyphens, and apostrophes")
        return v

    @validator("middle_name", "preferred_name")
    def validate_optional_name(cls, v):
        if v and not all(c.isalpha() or c.isspace() or c in "-'" for c in v):
            raise ValueError("Name must contain only letters, spaces, hyphens, and apostrophes")
        return v

    @validator("date_of_birth")
    def validate_date_of_birth(cls, v):
        today = date.today()
        if v > today:
            raise ValueError("date_of_birth cannot be in the future")
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Taxpayer must be at least 18 years old")
        if age > 150:
            raise ValueError("date_of_birth indicates age over 150 years")
        return v

    @validator("postal_code")
    def validate_postal_code(cls, v):
        if v:
            clean_postal = v.replace(" ", "").upper()
            if len(clean_postal) != 6:
                raise ValueError("Postal code must be 6 characters")
            return f"{clean_postal[:3]} {clean_postal[3:]}"
        return v

    @validator("phone_primary", "phone_secondary", "emergency_contact_phone")
    def validate_phone_number(cls, v):
        if v:
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10 or len(clean_phone) > 15:
                raise ValueError("Phone number must be between 10 and 15 digits")
            return clean_phone
        return v

    @validator("drivers_license_province", always=True)
    def validate_drivers_license_province(cls, v, values):
        license_num = values.get("drivers_license_number")
        if license_num and not v:
            raise ValueError("drivers_license_province is required when drivers_license_number is provided")
        return v

    @validator("emergency_contact_phone", always=True)
    def validate_emergency_contact_phone(cls, v, values):
        contact_name = values.get("emergency_contact_name")
        if contact_name and not v:
            raise ValueError("emergency_contact_phone is required when emergency_contact_name is provided")
        return v

    @validator("emergency_contact_relationship", always=True)
    def validate_emergency_contact_relationship(cls, v, values):
        contact_name = values.get("emergency_contact_name")
        if contact_name and not v:
            raise ValueError("emergency_contact_relationship is required when emergency_contact_name is provided")
        return v

    @validator("preferred_contact_method")
    def validate_contact_method(cls, v):
        if v:
            valid_methods = ["Email", "Phone", "Mail"]
            if v not in valid_methods:
                raise ValueError(f"preferred_contact_method must be one of {valid_methods}")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        if v:
            valid_genders = ["Male", "Female", "Non-binary", "Other", "Prefer not to say"]
            if v not in valid_genders:
                raise ValueError(f"gender must be one of {valid_genders}")
        return v
