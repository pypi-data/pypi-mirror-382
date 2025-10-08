from pydantic import BaseModel, Field, confloat,validator


# -------------------------------
# Support Payments & Contributions
# -------------------------------
class SupportAndContributions(BaseModel):
    child_support_received: confloat(ge=0) = Field(default=0.0) # type: ignore
    child_support_paid: confloat(ge=0) = Field(default=0.0) # type: ignore
    spousal_support_received: confloat(ge=0) = Field(default=0.0) # type: ignore
    spousal_support_paid: confloat(ge=0) = Field(default=0.0) # type: ignore
    rrsp_contributions: confloat(ge=0) = Field(default=0.0) # type: ignore
    union_dues: confloat(ge=0) = Field(default=0.0) # type: ignore
    professional_dues: confloat(ge=0) = Field(default=0.0) # type: ignore

    @validator("*", pre=True)
    def validate_support_amounts(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 10_000_000:
                raise ValueError("Support/Contribution amount exceeds maximum reasonable value")
        return v