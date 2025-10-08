from pydantic import BaseModel, Field, confloat,validator

# -------------------------------
# Core Income Sources
# -------------------------------
class IncomeInfo(BaseModel):
    net_income: confloat(ge=0) = Field(default=0.0) # type: ignore
    employment_income: confloat(ge=0) = Field(default=0.0) # type: ignore
    self_employment_income: confloat(ge=0) = Field(default=0.0) # type: ignore
    investment_income: confloat(ge=0) = Field(default=0.0) # type: ignore
    rental_income: confloat(ge=0) = Field(default=0.0) # type: ignore
    pension_income: confloat(ge=0) = Field(default=0.0) # type: ignore
    social_assistance_income: confloat(ge=0) = Field(default=0.0) # type: ignore
    other_income: confloat(ge=0) = Field(default=0.0) # type: ignore

    @validator("net_income")
    def validate_net_income(cls, v):
        v = round(v, 2)
        if v > 10_000_000:
            raise ValueError("net_income exceeds maximum reasonable value")
        return v

    @validator(
        "employment_income", "self_employment_income", "investment_income",
        "rental_income", "pension_income", "social_assistance_income", "other_income"
    )
    def validate_income_amounts(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 10_000_000:
                raise ValueError("Income amount exceeds maximum reasonable value")
        return v
