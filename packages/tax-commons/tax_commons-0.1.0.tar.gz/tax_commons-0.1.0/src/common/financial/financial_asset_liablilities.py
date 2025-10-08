from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, confloat, constr, validator



# -------------------------------
# Assets & Liabilities
# -------------------------------
class AssetsLiabilities(BaseModel):
    total_assets: confloat(ge=0) = Field(default=0.0) # type: ignore
    total_liabilities: confloat(ge=0) = Field(default=0.0) # type: ignore

    @validator("total_assets", "total_liabilities")
    def validate_assets_liabilities(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 100_000_000:
                raise ValueError("Asset/Liability amount exceeds maximum reasonable value")
        return v
