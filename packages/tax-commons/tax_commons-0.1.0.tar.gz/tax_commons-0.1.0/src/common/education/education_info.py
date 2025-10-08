from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

from common.education.education_credits import EducationCredits
from common.education.education_enrolment_info import EnrollmentInfo
from common.education.education_expenses import EducationExpenses
from common.education.education_forms import EducationForms
from common.education.education_tuition_info import TuitionInfo

# -------------------------------
# Main Education Info Model
# -------------------------------
class EducationInfo(BaseModel):
    tuition_info: TuitionInfo = Field(default_factory=TuitionInfo)
    enrollment_info: EnrollmentInfo = Field(default_factory=EnrollmentInfo)
    education_expenses: EducationExpenses = Field(default_factory=EducationExpenses)
    education_credits: EducationCredits = Field(default_factory=EducationCredits)
    education_forms: EducationForms = Field(default_factory=EducationForms)
    created_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    education_notes: Optional[constr(strip_whitespace=True, max_length=1000)] = None # type: ignore

    @validator("education_notes")
    def validate_education_notes(cls, v):
        if v:
            v = v.strip()
            if len(v) == 0:
                raise ValueError("education_notes cannot be empty if provided")
        return v
    
    @validator("enrollment_info", always=True)
    def validate_enrollment_info(cls, v, values):
        tuition = values.get("tuition_info").tuition_paid
        if tuition and tuition > 0:
            if not v.enrollment_status:
                raise ValueError("enrollment_status is required when tuition is paid")
            if not v.months_in_study or v.months_in_study == 0:
                raise ValueError("months_in_study is required when tuition is paid")
        return v
    
    @validator("education_credits", always=True)
    def validate_education_credits(cls, v, values):
        tuition = values.get("tuition_info").tuition_paid
        interest = values.get("education_expenses").student_loan_interest
        if v.eligible_for_tuition_credit and (tuition is None or tuition == 0):
            raise ValueError("Cannot claim tuition credit without tuition paid")
        if v.eligible_for_student_loan_interest_credit and (interest is None or interest == 0):
            raise ValueError("Cannot claim student loan interest credit without interest paid")
        return v
    
    @validator("education_forms", always=True)
    def validate_education_forms(cls, v, values):
        if v.t2202_form_available and not v.t2202_form_number:
            raise ValueError("t2202_form_number is required when T2202 form is available")
        if v.international_student and not v.study_permit_number:
            raise ValueError("study_permit_number is required for international students")
        return v
    
    @validator("tuition_info", always=True)
    def validate_tuition_info(cls, v):
        tuition = v.tuition_paid
        institution = v.education_institution
        if tuition and tuition > 0 and not institution:
            raise ValueError("education_institution is required if tuition_paid > 0")
        return v
    
    @validator("enrollment_info", always=True)
    def validate_enrollment_dates(cls, v):
        start = v.study_period_start
        end = v.study_period_end
        if start and end and end < start:
            raise ValueError("study_period_end must be after study_period_start")
        return v
    
    @validator("education_expenses", always=True)
    def validate_education_expenses(cls, v):
        for field_name, value in v:
            if value is not None:
                rounded_value = round(value, 2)
                if rounded_value > 100_000:
                    raise ValueError(f"{field_name} exceeds maximum reasonable value")
        return v
    
    @validator("created_by", "last_modified_by")
    def validate_user_fields(cls, v):
        v = v.strip()
        if len(v) == 0:
            raise ValueError("User fields cannot be empty")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "tuition_info": {
                    "tuition_paid": 5000.00,
                    "education_institution": "University of Example",
                    "institution_type": "University",
                    "program_name": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "education_level": "Undergraduate"
                },
                "enrollment_info": {
                    "enrollment_status": "Full-time",
                    "student_id": "U12345678",
                    "study_period_start": "2023-09-01",
                    "study_period_end": "2024-04-30",
                    "months_in_study": 8
                },
                "education_expenses": {
                    "textbooks_expenses": 800.00,
                    "mandatory_fees": 300.00,
                    "student_loan_interest": 150.00,
                    "scholarships_received": 1000.00,
                    "bursaries_received": 500.00,
                    "grants_received": 2000.00,
                    "transferred_tuition_amount": 0.00,
                    "carried_forward_tuition_amount": 2000.00
                },
                "education_credits": {
                    "eligible_for_education_credit": True,
                    "eligible_for_tuition_credit": True,
                    "eligible_for_student_loan_interest_credit": True
                },
                "education_forms": {
                    "t2202_form_available": True,
                    "t2202_form_number": "T2202-2023-0001",
                    "international_student": False,
                    "study_permit_number": None
                },
                "created_by": "system",
                "created_at": "2024-01-01T00:00:00Z",
                "last_modified_by": "system",
                "last_modified_at": "2024-01-01T00:00:00Z",
                "education_notes": "First year of computer science program."
            }
        }
    
