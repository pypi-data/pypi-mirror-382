from enum import Enum
from typing import Any, Dict, Optional
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, constr
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
def serialize_dependent_info(dependent_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB dependent_info into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    if "_id" in dependent_info:
        dependent_info["id"] = str(dependent_info["_id"]) if isinstance(dependent_info["_id"], ObjectId) else dependent_info["_id"]
        del dependent_info["_id"]
    return jsonable_encoder(dependent_info)


# ==================== Component Class ====================
class DependencyInformation(BaseModel):
    """Dependency status and benefit eligibility"""

    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50) # type: ignore
    
    # Dependency flags
    is_dependent: Optional[bool] = None
    eligible_for_canada_child_benefit: Optional[bool] = None
    eligible_for_disability_tax_credit: Optional[bool] = None
    eligible_for_child_care_expense: Optional[bool] = None
    eligible_for_eligible_dependant_amount: Optional[bool] = None
    eligible_for_caregiver_amount: Optional[bool] = None
    eligible_for_infirm_dependant_amount: Optional[bool] = None

    # Additional info
    claimed_as_dependent_by: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None # type: ignore
    relationship_to_claimant: Optional[RelationshipType] = None

    # Optional audit info
    audit: Optional[AuditInfo] = None

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
