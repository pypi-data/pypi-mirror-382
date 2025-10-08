from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator

# --- Disability Details ---
class DisabilityInfo(BaseModel):
    has_disability: bool = Field(default=False)
    disability_tax_credit_certificate: Optional[
        constr(strip_whitespace=True, min_length=1, max_length=100) # type: ignore
    ] = None  # type: ignore

    @validator("disability_tax_credit_certificate", always=True)
    def validate_disability_certificate(cls, v, values):
        if values.get("has_disability") and not v:
            raise ValueError(
                "disability_tax_credit_certificate is required when has_disability is True"
            )
        return v