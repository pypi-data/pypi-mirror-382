from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import date


class BusinessInformation(BaseModel):
    """Comprehensive business identity record for tax filing and compliance purposes"""

    # Basic business context
    business_name: Optional[str] = Field(None, description="Registered business/entity name")
    business_alias: Optional[str] = Field(None, description="Operating or trade name (if different from registered name)")
    business_tax_id: Optional[str] = Field(None, description="Business tax ID or registration number")
    business_registration_number: Optional[str] = Field(None, description="Company registration number (if applicable)")
    business_type: Optional[str] = Field(None, description="Type of business (e.g., LLC, Private Limited, Sole Proprietorship)")
    industry_sector: Optional[str] = Field(None, description="Industry or sector of operation")
    year_founded: Optional[int] = Field(None, description="Year the business was established")

    # Contact information
    business_email: Optional[EmailStr] = Field(None, description="Primary business email")
    business_phone: Optional[str] = Field(None, description="Primary business phone number")
    business_website: Optional[str] = Field(None, description="Official business website")
    business_address: Optional[str] = Field(None, description="Registered business address")
    city: Optional[str] = Field(None, description="City of business location")
    state: Optional[str] = Field(None, description="State/Province of business location")
    postal_code: Optional[str] = Field(None, description="Postal or ZIP code")
    country: Optional[str] = Field(None, description="Country of business operation")

    # Record metadata
    created_date: date = Field(default_factory=date.today, description="Date record was created")
    last_modified: Optional[date] = Field(None, description="Last modification date")
    filed_with_taxes: bool = Field(False, description="Whether included in filed tax return")

    @field_validator("last_modified")
    def validate_last_modified(cls, v, values):
        if v and v < values.get("created_date"):
            raise ValueError("Last modified date cannot be before created date")
        return v

    @field_validator("year_founded")
    def validate_year_founded(cls, v):
        if v and (v < 1800 or v > date.today().year):
            raise ValueError("Year founded must be reasonable")
        return v
