from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

from common.medical.medical_disability_info import DisabilityInfo
from common.medical.medical_expenses import MedicalExpenses
from common.medical.medical_practioner_info import MedicalPractitionerInfo
from common.education.status_info import AuditInfo

# --- Aggregate Medical Info ---
class MedicalInfo(BaseModel):
    disability: DisabilityInfo
    expenses: MedicalExpenses
    practitioner: MedicalPractitionerInfo
    audit: AuditInfo
    last_modified_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    medical_notes: Optional[constr(strip_whitespace=True, max_length=1000)] = None  # type: ignore

    @validator("medical_notes")
    def validate_medical_notes(cls, v):
        if v:
            v = v.strip()
            if len(v) == 0:
                raise ValueError("medical_notes cannot be empty if provided")
        return v
    
    @validator("practitioner", always=True)
    def validate_practitioner_info(cls, v, values):
        expenses = values.get("expenses").eligible_medical_expenses
        if expenses and expenses > 0 and not v.medical_practitioner_name:
            raise ValueError("medical_practitioner_name is required if eligible_medical_expenses > 0")
        return v
    
    @validator("disability", always=True)
    def validate_disability_info(cls, v, values):
        if v.has_disability and (not v.disability_tax_credit_certificate):
            raise ValueError("disability_tax_credit_certificate is required when has_disability is True")
        return v
    
    @validator("expenses", always=True)
    def validate_total_medical_expenses(cls, v):
        total = (
            v.attendant_care_expenses + v.nursing_home_expenses + v.prescription_expenses +
            v.dental_expenses + v.vision_expenses + v.medical_equipment_expenses +
            v.medical_travel_expenses + v.other_medical_expenses
        )
        if round(total, 2) != round(v.eligible_medical_expenses, 2):
            raise ValueError("Sum of individual medical expenses must equal eligible_medical_expenses")
        return v
    
    @validator("practitioner", always=True)
    def validate_practitioner_name(cls, v, values):
        expenses = values.get("expenses").eligible_medical_expenses
        if expenses and expenses > 0 and not v.medical_practitioner_name:
            raise ValueError("medical_practitioner_name is required if eligible_medical_expenses > 0")
        return v
    
    @validator("practitioner", always=True)
    def validate_medical_notes_in_practitioner(cls, v):
        if v.medical_notes:
            v.medical_notes = v.medical_notes.strip()
            if len(v.medical_notes) == 0:
                raise ValueError("medical_notes in practitioner cannot be empty if provided")
        return v
    
    @validator("last_modified_by")
    def validate_last_modified_by(cls, v):
        v = v.strip()
        if len(v) == 0:
            raise ValueError("last_modified_by cannot be empty")
        return v
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

