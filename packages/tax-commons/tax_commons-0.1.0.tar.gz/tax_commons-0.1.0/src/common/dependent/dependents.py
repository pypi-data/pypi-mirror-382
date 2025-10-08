from typing import Any, Dict, Optional
import uuid
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, constr

from src.helpers.helpers import AuditInfo
from src.common.dependent.child.dependent_child_care_information import ChildcareInformation
from src.common.dependent.child.dependent_child_custody_info import CustodyInformation
from src.common.dependent.child.dependent_child_support_payments import SupportPayments
from src.common.dependent.dependent_financial_information import FinancialInformation
from src.common.dependent.dependent_info import DependencyInformation
from src.common.dependent.dependent_living_arrangement import LivingArrangement
from src.common.dependent.dependent_relationship_details import RelationshipDetails
from src.common.dependent.dependent_relationship_info import RelationshipInfo
from src.common.dependent.spouse.dependent_marital_status import MaritalStatusDetails
from src.common.dependent.spouse.dependent_spouse_info import SpouseInfo

# ==================== Serialization Helper ====================
def serialize_dependents(dependents: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB dependents document into a JSON-serializable dict.
    - Renames `_id` to `id`
    - Converts ObjectId to string
    - Converts datetime and other non-JSON-safe types using FastAPI's jsonable_encoder
    """
    data = dependents.copy()
    if "_id" in data:
        data["id"] = str(data["_id"]) if isinstance(data["_id"], ObjectId) else data["_id"]
        del data["_id"]
    return jsonable_encoder(data)


# ==================== Main Dependent Model ====================
class Dependent(BaseModel):
    """
    Complete dependent information model.
    All fields are optional to support partial updates except dependent_id if provided.
    """

    # Optional ID fields
    taxpayer_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    dependent_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore

    # Optional component models
    dependent_info: Optional[DependencyInformation] = None
    dependent_living_arrangement: Optional[LivingArrangement] = None
    dependent_relationship_info: Optional[RelationshipInfo] = None
    dependent_relationship_detail: Optional[RelationshipDetails] = None
    dependent_financial_information: Optional[FinancialInformation] = None
    child_support_payments: Optional[SupportPayments] = None
    child_custody_information: Optional[CustodyInformation] = None
    child_care_information: Optional[ChildcareInformation] = None
    dependent_marital_status_details: Optional[MaritalStatusDetails] = None
    dependent_spouse_info: Optional[SpouseInfo] = None

    # Optional boolean flags
    dependent_is_spouse: Optional[bool] = None
    dependent_age_less_than_18: Optional[bool] = None
    dependent_requires_child_support: Optional[bool] = None
    tax_payer_is_divorced_or_separated: Optional[bool] = None
    tax_payer_has_child_custody: Optional[bool] = None

    # Optional audit information
    audit: Optional[AuditInfo] = None

    # ==================== Config ====================
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            uuid.UUID: str,
        }
        schema_extra = {
            "example": {
                "dependent_id": "a3f90f72-6e0d-4a93-b79e-7f07e5fa3d2d",
                "taxpayer_id": "TAX-12345",
                "dependent_info": {
                    "first_name": "Emma",
                    "last_name": "Johnson",
                    "date_of_birth": "2015-06-15"
                },
                "dependent_age_less_than_18": True,
                "dependent_is_spouse": False,
                "audit": {
                    "created_by": "user@example.com",
                    "created_at": "2025-01-15T10:30:00Z"
                }
            }
        }
