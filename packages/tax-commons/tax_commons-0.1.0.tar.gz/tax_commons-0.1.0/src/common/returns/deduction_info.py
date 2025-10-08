# --- Deduction Information ---
from pydantic import BaseModel, validator,confloat,Field

class DeductionInfo(BaseModel):
    rrsp_deduction: confloat(ge=0) = Field(default=0.0)  # type: ignore
    union_dues: confloat(ge=0) = Field(default=0.0)  # type: ignore
    child_care_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore
    moving_expenses: confloat(ge=0) = Field(default=0.0)  # type: ignore

    @validator("rrsp_deduction", "union_dues", "child_care_expenses", "moving_expenses")
    def validate_deduction_amounts(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 10_000_000:
                raise ValueError("Deduction amount exceeds maximum reasonable value")
        return v
