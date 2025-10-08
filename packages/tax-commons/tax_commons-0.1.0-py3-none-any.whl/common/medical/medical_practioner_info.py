from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, confloat, constr, validator

from common.education.status_info import AuditInfo

# --- Enums ---
class MedicalPractitionerType(str, Enum):
    PHYSICIAN = "Physician"
    SPECIALIST = "Specialist"
    PSYCHIATRIST = "Psychiatrist"
    PSYCHOLOGIST = "Psychologist"
    NURSE_PRACTITIONER = "Nurse Practitioner"
    PHYSIOTHERAPIST = "Physiotherapist"
    OCCUPATIONAL_THERAPIST = "Occupational Therapist"
    CHIROPRACTOR = "Chiropractor"
    DENTIST = "Dentist"
    OPTOMETRIST = "Optometrist"
    PHARMACIST = "Pharmacist"
    OTHER = "Other"
    
# --- Medical Practitioner Info ---
class MedicalPractitionerInfo(BaseModel):
    # Primary Medical Practitioner
    medical_practitioner_type: Optional[MedicalPractitionerType] = None
    medical_practitioner_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    medical_practitioner_license: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    medical_practice_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    
    # Contact Information
    medical_practitioner_phone: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None # type: ignore
    medical_practitioner_fax: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None # type: ignore
    medical_practitioner_email: Optional[EmailStr] = None
    
    # Address Information
    medical_office_address: Optional[constr(strip_whitespace=True, min_length=1, max_length=500)] = None # type: ignore
    medical_office_city: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore
    medical_office_province: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore
    medical_office_postal_code: Optional[constr(strip_whitespace=True, pattern=r'^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$')] = None # type: ignore

    medical_notes: Optional[constr(strip_whitespace=True, max_length=1000)] = None # type: ignore
    audit_info: AuditInfo = Field(default_factory=AuditInfo)

    @validator("medical_practitioner_phone", "medical_practitioner_fax")
    def validate_phone_number(cls, v):
        if v:
            clean_number = v.replace(" ", "").replace("-", "")
            if not (10 <= len(clean_number) <= 15) or not clean_number.lstrip('+').isdigit():
                raise ValueError("Phone number must be 10 to 15 digits, optionally starting with +")
            return clean_number
        return v
    
    @validator("medical_office_postal_code")
    def validate_postal_code(cls, v):
        if v:
            clean_code = v.replace(" ", "").upper()
            if len(clean_code) != 6:
                raise ValueError("Postal code must be 6 characters")
            if not (clean_code[0].isalpha() and clean_code[1].isdigit() and 
                    clean_code[2].isalpha() and clean_code[3].isdigit() and 
                    clean_code[4].isalpha() and clean_code[5].isdigit()):
                raise ValueError("Postal code must follow format A1A 1A1")
            return f"{clean_code[:3]} {clean_code[3:]}"
        return v
    
    @validator("medical_practitioner_name", "medical_practice_name")
    def validate_name_fields(cls, v):
        if v and not v.strip():
            raise ValueError("Name cannot be only whitespace")
        return v
    
    @validator("medical_practitioner_license")
    def validate_license(cls, v):
        if v and not v.strip():
            raise ValueError("License cannot be only whitespace")
        return v
    
    @validator("medical_office_city", "medical_office_province")
    def validate_location_fields(cls, v):   
        if v and not v.strip():
            raise ValueError("Location fields cannot be only whitespace")
        return v
