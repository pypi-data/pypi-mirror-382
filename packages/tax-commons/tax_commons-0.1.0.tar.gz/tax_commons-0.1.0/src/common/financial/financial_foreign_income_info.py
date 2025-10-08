from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

# -------------------------------
# Foreign Income
# -------------------------------
class ForeignIncome(BaseModel):
    has_foreign_income: bool = Field(default=False)
    foreign_income_amount: confloat(ge=0) = Field(default=0.0) # type: ignore
    foreign_country: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore

    @validator("foreign_income_amount", always=True)
    def validate_foreign_income(cls, v, values):
        if values.get("has_foreign_income") and v == 0:
            raise ValueError("foreign_income_amount must be > 0 when has_foreign_income is True")
        return v

    @validator("foreign_country", always=True)
    def validate_foreign_country(cls, v, values):
        if values.get("has_foreign_income") and not v:
            raise ValueError("foreign_country is required when has_foreign_income is True")
        return v

