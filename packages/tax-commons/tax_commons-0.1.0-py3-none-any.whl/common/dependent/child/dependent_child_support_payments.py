from datetime import date
from enum import Enum
from typing import Any, Dict, Optional
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, validator, Field, confloat, constr

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
def serialize_dependent_child_support_payments(dependent_child_support_payments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB dependent_child_support_payments into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    if "_id" in dependent_child_support_payments:
        dependent_child_support_payments["id"] = str(dependent_child_support_payments["_id"]) if isinstance(dependent_child_support_payments["_id"], ObjectId) else dependent_child_support_payments["_id"]
        del dependent_child_support_payments["_id"]
    return jsonable_encoder(dependent_child_support_payments)


# ==================== Main Model ====================
class SupportPayments(BaseModel):
    """Child and spousal support payment information"""
    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50) # type: ignore
    child_support_paid: Optional[confloat(ge=0)] = Field(default=0.0) # type: ignore
    child_support_received: Optional[confloat(ge=0)] = Field(default=0.0) # type: ignore
    spousal_support_paid: Optional[confloat(ge=0)] = Field(default=0.0) # type: ignore
    spousal_support_received: Optional[confloat(ge=0)] = Field(default=0.0) # type: ignore
    court_order_number: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None # type: ignore
    separation_agreement_date: Optional[date] = None
    audit: AuditInfo

    # ==================== Validators ====================
    @validator("child_support_paid", "child_support_received", "spousal_support_paid", "spousal_support_received")
    def validate_support_amounts(cls, v):
        if v is not None:
            v = round(v, 2)
            if v > 10_000_000:
                raise ValueError("Support amount exceeds maximum reasonable value")
        return v

    @validator("court_order_number")
    def validate_court_order_number(cls, v):
        if v:
            v = v.strip()
            if len(v) == 0:
                raise ValueError("court_order_number cannot be empty if provided")
        return v

    @validator("separation_agreement_date")
    def validate_separation_date(cls, v):
        if v and v > date.today():
            raise ValueError("separation_agreement_date cannot be in the future")
        return v
