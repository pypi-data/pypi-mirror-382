from datetime import date
from typing import Optional
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, Field, constr, validator

class AuthorizationConsent(BaseModel):
    """Authorization and consent tracking"""
    authorize_cra_communication: bool = Field(default=False)
    authorize_third_party_disclosure: bool = Field(default=False)
    consent_to_electronic_filing: bool = Field(default=True)
    consent_to_data_storage: bool = Field(default=True)
    consent_to_marketing: bool = Field(default=False)
    privacy_policy_accepted: bool = Field(default=False)
    privacy_policy_accepted_date: Optional[date] = None
    terms_of_service_accepted: bool = Field(default=False)
    terms_of_service_accepted_date: Optional[date] = None

    @validator("privacy_policy_accepted_date", always=True)
    def validate_privacy_policy_date(cls, v, values):
        accepted = values.get("privacy_policy_accepted")
        if accepted and not v:
            raise ValueError("privacy_policy_accepted_date is required when privacy_policy_accepted is True")
        return v

    @validator("terms_of_service_accepted_date", always=True)
    def validate_terms_date(cls, v, values):
        accepted = values.get("terms_of_service_accepted")
        if accepted and not v:
            raise ValueError("terms_of_service_accepted_date is required when terms_of_service_accepted is True")
        return v