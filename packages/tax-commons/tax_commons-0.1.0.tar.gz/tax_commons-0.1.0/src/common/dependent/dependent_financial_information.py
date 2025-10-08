from typing import Any, Dict, Optional
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, validator, constr
from common.education.status_info import AuditInfo


# ==================== Serialization Helper ====================
def serialize_financial_info(financial_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB financial_info document into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    if "_id" in financial_info:
        financial_info["id"] = str(financial_info["_id"]) if isinstance(financial_info["_id"], ObjectId) else financial_info["_id"]
        del financial_info["_id"]
    return jsonable_encoder(financial_info)


# ==================== Main Model ====================
class FinancialInformation(BaseModel):
    """
    Income and financial support information for dependents.
    All fields except `dependent_id` are optional.
    """
    
    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50) # type: ignore
    
    # Optional income fields
    net_income: Optional[float] = Field(default=None, ge=0)
    employment_income: Optional[float] = Field(default=None, ge=0)
    other_income: Optional[float] = Field(default=None, ge=0)

    # Optional support and assistance flags
    receives_social_assistance: Optional[bool] = None
    taxpayer_provides_support: Optional[bool] = None

    # Optional support amounts
    support_amount_provided: Optional[float] = Field(default=None, ge=0)
    percentage_support_provided: Optional[int] = Field(default=None, ge=0, le=100)

    # Optional audit info
    audit: Optional[AuditInfo] = None

    # ==================== Validators ====================
    @validator("net_income", "employment_income", "other_income", "support_amount_provided", pre=True)
    def validate_financial_amounts(cls, v):
        if v is not None:
            v = round(float(v), 2)
            if v > 10_000_000:
                raise ValueError("Financial amount exceeds maximum reasonable value of $10,000,000")
        return v

    @validator("support_amount_provided", always=True)
    def validate_support_amount(cls, v, values):
        provides_support = values.get("taxpayer_provides_support")
        if provides_support is True and (v is None or v <= 0):
            raise ValueError("support_amount_provided must be greater than 0 when taxpayer_provides_support is True")
        return v

    @validator("percentage_support_provided")
    def validate_support_percentage(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError("percentage_support_provided must be between 0 and 100")
        return v

    @validator("net_income", always=True)
    def validate_net_income_consistency(cls, v, values):
        employment = values.get("employment_income") or 0
        other = values.get("other_income") or 0
        if v is not None and (employment > 0 or other > 0):
            total_declared = employment + other
            # Allow 10% tolerance
            if v < total_declared * 0.9:
                # Could log a warning or handle according to business rules
                pass
        return v

    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            float: lambda v: round(v, 2) if v is not None else None,
        }
