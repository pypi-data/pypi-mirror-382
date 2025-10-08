from typing import Optional
import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class TaxHistory(BaseModel):
    """Tax filing history"""
    years_as_client: int = Field(default=0, ge=0)
    first_filing_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    most_recent_filing_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    total_returns_filed: int = Field(default=0, ge=0)
    returns_under_review: int = Field(default=0, ge=0)
    returns_reassessed: int = Field(default=0, ge=0)
    outstanding_returns: int = Field(default=0, ge=0)

    @validator("most_recent_filing_year", always=True)
    def validate_filing_years(cls, v, values):
        first_year = values.get("first_filing_year")
        if first_year and v and v < first_year:
            raise ValueError("most_recent_filing_year cannot be before first_filing_year")
        return v

    @validator("years_as_client", "total_returns_filed", "returns_under_review",
               "returns_reassessed", "outstanding_returns")
    def validate_non_negative_counts(cls, v):
        if v < 0:
            raise ValueError("Count fields cannot be negative")
        return v
