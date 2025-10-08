from enum import Enum
from typing import Any, Dict, Optional
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, constr, confloat, validator

from common.education.status_info import AuditInfo


# ==================== Enums ====================
class RelationshipType(str, Enum):
    CHILD = "Child"
    STEPCHILD = "Stepchild"
    GRANDCHILD = "Grandchild"
    SIBLING = "Sibling"
    NIECE_NEPHEW = "Niece/Nephew"
    PARENT = "Parent"
    GRANDPARENT = "Grandparent"
    SPOUSE = "Spouse"
    COMMON_LAW_PARTNER = "Common-Law Partner"
    OTHER = "Other"


# ==================== Serialization Helper ====================
def serialize_dependent_child_care_info(dependent_child_care_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB dependent_child_care_info into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    if "_id" in dependent_child_care_info:
        dependent_child_care_info["id"] = str(dependent_child_care_info["_id"]) if isinstance(dependent_child_care_info["_id"], ObjectId) else dependent_child_care_info["_id"]
        del dependent_child_care_info["_id"]
    return jsonable_encoder(dependent_child_care_info)


# ==================== Main Model ====================
class ChildcareInformation(BaseModel):
    """Childcare expenses and provider information"""
    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50)  # type: ignore
    child_care_expenses_paid: Optional[confloat(ge=0)] = Field(default=0.0)  # type: ignore
    child_care_provider_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None  # type: ignore
    child_care_provider_sin: Optional[constr(strip_whitespace=True, pattern=r'^\d{9}$')] = None  # type: ignore
    child_care_provider_business_number: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    child_care_provider_address: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None  # type: ignore
    child_care_provider_city: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    child_care_provider_province: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None  # type: ignore
    child_care_provider_postal_code: Optional[constr(strip_whitespace=True, pattern=r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$')] = None  # type: ignore
    child_care_provider_phone: Optional[constr(strip_whitespace=True, pattern=r'^\+?1?\d{10,15}$')] = None  # type: ignore
    audit: AuditInfo

    # ==================== Validators ====================
    @validator("child_care_expenses_paid")
    def validate_childcare_expenses(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 10_000_000:
                raise ValueError("Childcare expense amount exceeds maximum reasonable value")
        return v

    @validator("child_care_provider_name", always=True)
    def validate_childcare_provider(cls, v, values):
        expenses = values.get("child_care_expenses_paid") or 0
        if expenses > 0 and not v:
            raise ValueError("child_care_provider_name is required when child_care_expenses_paid > 0")
        return v

    @validator("child_care_provider_sin")
    def validate_provider_sin(cls, v):
        if v:
            clean_sin = v.replace(" ", "").replace("-", "")
            if len(clean_sin) != 9 or not clean_sin.isdigit():
                raise ValueError("SIN must be 9 digits")

            # Luhn checksum validation
            def luhn_checksum(sin_str):
                digits = [int(d) for d in sin_str]
                checksum = sum(digits[-1::-2]) + sum(sum(divmod(d * 2, 10)) for d in digits[-2::-2])
                return checksum % 10

            if luhn_checksum(clean_sin) != 0:
                raise ValueError("Invalid SIN checksum")
            return clean_sin
        return v
