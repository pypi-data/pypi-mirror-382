from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, constr, validator

from src.common.dependent.child.dependent_child_care_information import ChildcareInformation
from src.common.dependent.child.dependent_child_custody_info import CustodyInformation
from src.common.dependent.child.dependent_child_support_payments import SupportPayments
from src.common.dependent.dependent_info import DependencyInformation
from src.common.dependent.dependent_living_arrangement import LivingArrangementInfo
from src.common.dependent.dependent_relationship_details import RelationshipDetails
from common.education.status_info import AuditInfo


# ==================== Serialization Helper ====================
def serialize_relationship_info(relationship_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a RelationshipInfo dict into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    data = relationship_info.copy()
    if "_id" in data:
        data["id"] = str(data["_id"]) if isinstance(data["_id"], ObjectId) else data["_id"]
        del data["_id"]
    return jsonable_encoder(data)


# ==================== Main Model ====================
class RelationshipInfo(BaseModel):
    """Complete relationship information, composing all dependent components"""

    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50)  # type: ignore
    relationship_id: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    relationship_name: Optional[str] = None
    relationship_details: Optional[RelationshipDetails] = None
    living_arrangement: Optional[LivingArrangementInfo] = None
    support_payments: Optional[SupportPayments] = None
    childcare_info: Optional[ChildcareInformation] = None
    custody_info: Optional[CustodyInformation] = None
    dependency_info: Optional[DependencyInformation] = None
    education_info_id: Optional[str] = None
    disability_info_id: Optional[str] = None
    contact_info_id: Optional[str] = None
    personal_info: Optional[str] = None
    financial_info: Optional[str] = None
    relationship_notes: Optional[str] = None
    audit: Optional[AuditInfo] = None

    # ==================== Validators ====================
    @validator("relationship_id")
    def validate_relationship_id(cls, v):
        if not v.strip():
            raise ValueError("relationship_id cannot be empty or whitespace")
        return v

    @validator(
        "relationship_name", "relationship_notes", "education_info_id",
        "disability_info_id", "contact_info_id", "personal_info", "financial_info",
        pre=True, always=True
    )
    def validate_nonempty_strings(cls, v):
        if v is not None and not v.strip():
            raise ValueError("String fields cannot be empty if provided")
        return v

    @validator("audit", always=True)
    def validate_audit_timestamps(cls, v):
        if not v:
            return v
        now = datetime.now(timezone.utc)
        if v.created_at and v.created_at > now:
            raise ValueError("audit.created_at cannot be in the future")
        if v.last_modified_at and v.last_modified_at > now:
            raise ValueError("audit.last_modified_at cannot be in the future")
        if v.created_at and v.last_modified_at and v.last_modified_at < v.created_at:
            raise ValueError("audit.last_modified_at cannot be before audit.created_at")
        return v

    # ==================== Serialization Method ====================
    def to_serializable_dict(self) -> Dict[str, Any]:
        """Convert the RelationshipInfo to a JSON-serializable dict."""
        return serialize_relationship_info(self.dict())

    # ==================== Config ====================
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "dependent_id": "DEP-67890",
                "relationship_id": "REL-2025-001",
                "relationship_name": "Child Relationship",
                "relationship_details": {"relationship": "Child"},
                "personal_info": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "date_of_birth": "2010-05-15"
                },
                "audit": {
                    "created_by": "system",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_modified_by": "system",
                    "last_modified_at": "2024-01-01T00:00:00Z"
                }
            }
        }
