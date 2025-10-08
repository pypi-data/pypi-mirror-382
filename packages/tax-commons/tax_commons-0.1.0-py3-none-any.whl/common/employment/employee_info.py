from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr, field_validator, validator
from datetime import date


from common.education.status_info import AuditInfo
from common.tax_payer.enums.employee_status import EmploymentStatus, EmploymentStatusType
from common.tax_payer.enums.employment_type import EmploymentType

class EmployeeInfo(BaseModel):
    tax_payer_id:  constr(min_length=1, max_length=255)  # type: ignore
    employer_id: constr(min_length=1, max_length=255)  # type: ignore
    employee_id: constr(min_length=1, max_length=255)  # type: ignore
    employee_number: constr(min_length=1, max_length=255)  # type: ignore
    date_of_joining: Optional[date]
    date_of_termination: Optional[date] = None
    job_title: Optional[str]
    department: Optional[str]
    employment_type: Optional[EmploymentType] = None
    is_active: bool = True

    employment_status: Optional[EmploymentStatus] = None
    employer_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    employer_ein: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    occupation: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None # type: ignore

    unemployment_start_date: Optional[date] = None
    retirement_date: Optional[date] = None

    @validator("employer_name", always=True)
    def validate_employer_name(cls, v, values):
        status = values.get("employment_status")
        if status in [EmploymentStatus.EMPLOYED_FULL_TIME, EmploymentStatus.EMPLOYED_PART_TIME] and not v:
            raise ValueError("employer_name is required for employed individuals")
        return v

    class Config:
        anystr_strip_whitespace = True
        schema_extra = {
            "example": {
                "employee_id": "EMP12345",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-15",
                "gender": "Male",
                "email": "john.doe@example.com",
                "phone_number": "+1234567890",
                "address": {
                    "street": "123 Main St",
                    "city": "Metropolis",
                    "state_province": "StateX",
                    "postal_code": "12345",
                    "country": "CountryX"
                },
                "previous_addresses": [],
                "date_of_joining": "2023-04-01",
                "job_title": "Software Engineer",
                "department": "Engineering",
                "manager_id": "EMP10001",
                "employment_type": "Full-Time",
                "skills": ["Python", "FastAPI", "Pydantic"],
                "certifications": ["AWS Certified Developer"],
                "emergency_contacts": [
                    {"name": "Jane Doe", "relationship": "Spouse", "phone_number": "+1234567891"}
                ],
                "is_active": True
            }
        }

    