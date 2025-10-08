from enum import Enum
from typing import Any, Dict, Optional
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, constr, validator

from common.education.status_info import AuditInfo


# ==================== Enums ====================
class CustodyType(str, Enum):
    SOLE_CUSTODY = "Sole Custody"
    JOINT_CUSTODY = "Joint Custody"
    SHARED_CUSTODY = "Shared Custody"
    NO_CUSTODY = "No Custody"


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
def serialize_dependent_child_custody_info(dependent_child_custody_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB dependent_child_custody_info into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    if "_id" in dependent_child_custody_info:
        dependent_child_custody_info["id"] = str(dependent_child_custody_info["_id"]) if isinstance(dependent_child_custody_info["_id"], ObjectId) else dependent_child_custody_info["_id"]
        del dependent_child_custody_info["_id"]
    return jsonable_encoder(dependent_child_custody_info)


# ==================== Main Model ====================
class CustodyInformation(BaseModel):
    """Custody arrangement for children"""
    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50) # type: ignore
    custody_type: Optional[CustodyType] = None # type: ignore
    custody_percentage: Optional[int] = Field(default=None, ge=0, le=100) # type: ignore
    other_parent_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None # type: ignore
    other_parent_sin: Optional[constr(strip_whitespace=True, pattern=r'^\d{9}$')] = None # type: ignore
    audit: AuditInfo

    # ==================== Validators ====================
    @validator("custody_percentage", always=True)
    def validate_custody_percentage(cls, v, values):
        custody_type = values.get("custody_type")
        if custody_type == CustodyType.SHARED_CUSTODY and v is None:
            raise ValueError("custody_percentage is required for shared custody")
        if v is not None and (v < 0 or v > 100):
            raise ValueError("custody_percentage must be between 0 and 100")
        return v

    @validator("other_parent_sin")
    def validate_other_parent_sin(cls, v):
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
