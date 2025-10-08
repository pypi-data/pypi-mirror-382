from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator, constr


class ProfessionalRepresentative(BaseModel):
    """Tax professional and representative information"""
    has_tax_professional: bool = Field(default=False)
    tax_professional_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    tax_professional_firm: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    tax_professional_license: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    tax_professional_phone: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None # type: ignore
    tax_professional_email: Optional[EmailStr] = None
    assigned_accountant: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    assigned_tax_preparer: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    case_manager: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore

    @validator("tax_professional_name", always=True)
    def validate_tax_professional_name(cls, v, values):
        has_professional = values.get("has_tax_professional")
        if has_professional and not v:
            raise ValueError("tax_professional_name is required when has_tax_professional is True")
        return v

    @validator("tax_professional_phone")
    def validate_professional_phone(cls, v):
        if v:
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 10 or len(clean_phone) > 15:
                raise ValueError("Phone number must be between 10 and 15 digits")
            return clean_phone
        return v