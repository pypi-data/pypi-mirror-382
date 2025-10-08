from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, constr, validator

from common.education.status_info import AuditInfo


# ==================== Serialization Helper ====================
def serialize_relationship_details(relationship_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB relationship_details document into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    if "_id" in relationship_details:
        relationship_details["id"] = (
            str(relationship_details["_id"]) if isinstance(relationship_details["_id"], ObjectId)
            else relationship_details["_id"]
        )
        del relationship_details["_id"]
    return jsonable_encoder(relationship_details)


# ==================== Enums ====================
class RelationshipType(str, Enum):
    """Types of relationships between taxpayer and dependent"""
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


# ==================== Main Model ====================
class RelationshipDetails(BaseModel):
    """
    Relationship type and details between taxpayer and dependent.
    All fields except IDs are optional to support partial updates.
    """

    relationship_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    taxpayer_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50)  # type: ignore
    
    relationship: Optional[RelationshipType] = None
    relationship_start_date: Optional[date] = None
    relationship_end_date: Optional[date] = None
    relationship_other_description: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None  # type: ignore
    
    audit: Optional[AuditInfo] = None

    # ==================== Validators ====================
    @validator("relationship_other_description", always=True)
    def validate_other_desc(cls, v, values):
        """Ensure description is provided when relationship is 'Other'"""
        if values.get("relationship") == RelationshipType.OTHER:
            if not v or not v.strip():
                raise ValueError("relationship_other_description is required when relationship is 'Other'")
        return v

    @validator("relationship_end_date")
    def validate_end_date(cls, v, values):
        """Ensure end_date is after start_date if both provided"""
        start_date = values.get("relationship_start_date")
        if v and start_date and v < start_date:
            raise ValueError("relationship_end_date must be after relationship_start_date")
        return v

    # ==================== Config ====================
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            date: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example_child": {
                "relationship_id": "REL-2025-001",
                "taxpayer_id": "TAX-12345",
                "dependent_id": "DEP-67890",
                "relationship": "Child",
                "relationship_start_date": "2015-06-15",
                "relationship_end_date": None,
                "relationship_other_description": None,
                "audit": {
                    "created_by": "user@example.com",
                    "created_at": "2025-01-15T10:30:00Z",
                    "last_modified_by": "user@example.com",
                    "last_modified_at": "2025-01-15T10:30:00Z"
                }
            },
            "example_other": {
                "relationship_id": "REL-2025-002",
                "taxpayer_id": "TAX-12345",
                "dependent_id": "DEP-99999",
                "relationship": "Other",
                "relationship_start_date": "2020-01-01",
                "relationship_end_date": None,
                "relationship_other_description": "Foster child under temporary care agreement",
                "audit": {
                    "created_by": "user@example.com",
                    "created_at": "2025-01-15T10:30:00Z",
                    "last_modified_by": "user@example.com",
                    "last_modified_at": "2025-01-15T10:30:00Z"
                }
            }
        }
