from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, validator, constr
from common.education.status_info import AuditInfo


# ==================== Enums ====================
class LivingArrangement(str, Enum):
    """Types of living arrangements for dependents"""
    LIVES_WITH_TAXPAYER = "Lives with Taxpayer"
    LIVES_SEPARATELY = "Lives Separately"
    SHARED_CUSTODY = "Shared Custody"
    TEMPORARY_ABSENCE = "Temporary Absence"


# ==================== Serialization Helper ====================
def serialize_living_arrangement_info(living_arrangement_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB living_arrangement_info document into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    if "_id" in living_arrangement_info:
        living_arrangement_info["id"] = (
            str(living_arrangement_info["_id"])
            if isinstance(living_arrangement_info["_id"], ObjectId)
            else living_arrangement_info["_id"]
        )
        del living_arrangement_info["_id"]
    return jsonable_encoder(living_arrangement_info)


# ==================== Main Model ====================
class LivingArrangementInfo(BaseModel):
    """
    Living arrangement details for dependents.
    All fields except IDs are optional to support partial updates.
    """
    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50) # type: ignore
    relationship_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore
    living_arrangement: Optional[LivingArrangement] = None
    lives_with_taxpayer: Optional[bool] = None
    months_lived_with_taxpayer: Optional[int] = Field(default=None, ge=0, le=12)
    moved_in_date: Optional[date] = None
    moved_out_date: Optional[date] = None
    audit: Optional[AuditInfo] = None

    # ==================== Validators ====================
    @validator("months_lived_with_taxpayer", always=True)
    def validate_months_lived(cls, v, values):
        lives_with = values.get("lives_with_taxpayer")
        if lives_with is True and v is None:
            raise ValueError("months_lived_with_taxpayer is required when lives_with_taxpayer is True")
        if v is not None and (v < 0 or v > 12):
            raise ValueError("months_lived_with_taxpayer must be between 0 and 12")
        return v

    @validator("moved_out_date", always=True)
    def validate_move_dates(cls, v, values):
        moved_in = values.get("moved_in_date")
        if moved_in and v and v < moved_in:
            raise ValueError("moved_out_date cannot be before moved_in_date")
        return v

    @validator("living_arrangement", always=True)
    def validate_living_arrangement_consistency(cls, v, values):
        lives_with = values.get("lives_with_taxpayer")
        if lives_with is True and v == LivingArrangement.LIVES_SEPARATELY:
            raise ValueError("living_arrangement cannot be 'Lives Separately' when lives_with_taxpayer is True")
        if lives_with is False and v == LivingArrangement.LIVES_WITH_TAXPAYER:
            raise ValueError("living_arrangement cannot be 'Lives with Taxpayer' when lives_with_taxpayer is False")
        return v

    @validator("months_lived_with_taxpayer")
    def validate_shared_custody_months(cls, v, values):
        if values.get("living_arrangement") == LivingArrangement.SHARED_CUSTODY and v == 12:
            # Allowed, but might be unusual → warning
            pass
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
            "example": {
                "dependent_id": "DEP-67890",
                "relationship_id": "REL-2025-001",
                "living_arrangement": "Lives with Taxpayer",
                "lives_with_taxpayer": True,
                "months_lived_with_taxpayer": 12,
                "moved_in_date": "2020-01-15",
                "moved_out_date": None,
                "audit": {
                    "created_by": "user@example.com",
                    "created_at": "2025-01-15T10:30:00Z",
                    "last_modified_by": "user@example.com",
                    "last_modified_at": "2025-01-15T10:30:00Z"
                }
            }
        }
