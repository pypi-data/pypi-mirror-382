from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, validator
import re


class EmployerAddress(BaseModel):
    street: constr(min_length=1)
    city: constr(min_length=1)
    state_province: Optional[constr(min_length=1)]
    postal_code: Optional[constr(min_length=3, max_length=20)]
    country: Optional[constr(min_length=2)]


class ContactPerson(BaseModel):
    name: constr(min_length=1)
    role: Optional[constr(min_length=1)]
    phone_number: Optional[str]
    email: Optional[EmailStr]

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if v is None:
            return v
        pattern = r'^\+?[0-9]{7,15}$'
        if not re.match(pattern, v):
            raise ValueError("Phone number must be 7-15 digits, optional leading +")
        return v


class EmployerInfo(BaseModel):
    employer_id: constr(min_length=1, max_length=255)
    employer_name: constr(min_length=1, max_length=200)
    employer_address: EmployerAddress
    contact_persons: Optional[List[ContactPerson]] = []
    is_active: bool = True
    departments: Optional[List[str]] = []
    additional_addresses: Optional[List[EmployerAddress]] = []

    # Custom validators
    @validator("departments", each_item=True)
    def department_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Department names cannot be empty")
        return v

    @validator("additional_addresses", each_item=True)
    def validate_additional_addresses(cls, v):
        if not isinstance(v, EmployerAddress):
            raise ValueError("Each additional address must be a valid EmployerAddress")
        return v

    class Config:
        anystr_strip_whitespace = True
        schema_extra = {
            "example": {
                "employer_id": "EMPLOYER123",
                "employer_name": "Tech Solutions Inc.",
                "employer_address": {
                    "street": "456 Corporate Blvd",
                    "city": "Metropolis",
                    "state_province": "StateX",
                    "postal_code": "12345",
                    "country": "CountryX"
                },
                "contact_persons": [
                    {
                        "name": "Jane Smith",
                        "role": "HR Manager",
                        "phone_number": "+1234567891",
                        "email": "jane.smith@techsolutions.com"
                    }
                ],
                "departments": ["Engineering", "HR", "Finance"],
                "additional_addresses": [],
                "is_active": True
            }
        }
