# --- Income Information ---
from pydantic import BaseModel, validator, Field, confloat

class IncomeInfo(BaseModel):
    total_income: confloat(ge=0) = Field(default=0.0)  # type: ignore
    net_income: confloat(ge=0) = Field(default=0.0)  # type: ignore
    taxable_income: confloat(ge=0) = Field(default=0.0)  # type: ignore
    employment_income: confloat(ge=0) = Field(default=0.0)  # type: ignore
    self_employment_income: confloat(ge=0) = Field(default=0.0)  # type: ignore
    interest_income: confloat(ge=0) = Field(default=0.0)  # type: ignore
    dividend_income: confloat(ge=0) = Field(default=0.0)  # type: ignore
    capital_gains: confloat(ge=0) = Field(default=0.0)  # type: ignore
    rental_income: confloat(ge=0) = Field(default=0.0)  # type: ignore

    @validator("total_income", "net_income", "taxable_income", "employment_income",
               "self_employment_income", "interest_income", "dividend_income",
               "capital_gains", "rental_income")
    def validate_income_amounts(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 100_000_000:
                raise ValueError("Income amount exceeds maximum reasonable value")
        return v

