from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

# --- Medical Expenses ---
class MedicalExpenses(BaseModel):
    eligible_medical_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    attendant_care_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    nursing_home_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    prescription_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    dental_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    vision_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    medical_equipment_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    medical_travel_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    other_medical_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore

    @validator("eligible_medical_expenses")
    def validate_medical_expenses(cls, v):
        v = round(v, 2)
        if v > 1_000_000:
            raise ValueError("eligible_medical_expenses exceeds maximum reasonable value")
        return v

    @validator(
        "attendant_care_expenses",
        "nursing_home_expenses",
        "prescription_expenses",
        "dental_expenses",
        "vision_expenses",
        "medical_equipment_expenses",
        "medical_travel_expenses",
        "other_medical_expenses",
    )
    def validate_expense_amounts(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 1_000_000:
                raise ValueError("Expense amount exceeds maximum reasonable value")
        return v
