from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, constr, validator

from common.education.status_info import AuditInfo


# ==================== Enum ====================
class MaritalStatus(str, Enum):
    MARRIED = "Married"
    COMMON_LAW = "Common-Law"
    SEPARATED = "Separated"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"


# ==================== Serialization Helper ====================
def serialize_marital_status(marital_status: Dict[str, Any]) -> Dict[str, Any]:
    if "_id" in marital_status:
        marital_status["id"] = (
            str(marital_status["_id"])
            if isinstance(marital_status["_id"], ObjectId)
            else marital_status["_id"]
        )
        del marital_status["_id"]
    return jsonable_encoder(marital_status)


# ==================== Main Model ====================
class MaritalStatusDetails(BaseModel):
    """Marital status and relationship dates"""

    dependent_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None # type: ignore

    marital_status: Optional[MaritalStatus] = None

    marriage_date: Optional[date] = None
    common_law_start_date: Optional[date] = None
    separation_date: Optional[date] = None
    divorce_date: Optional[date] = None
    date_of_death: Optional[date] = None

    lived_together_all_year: Optional[bool] = None
    months_lived_together: Optional[int] = Field(default=None, ge=0, le=12)
    reconciliation_occurred: Optional[bool] = None
    reconciliation_date: Optional[date] = None

    audit_info: Optional[AuditInfo] = None

    # ---------------- Validators ---------------- #
    @validator("marriage_date", always=True)
    def validate_marriage_date(cls, v, values):
        if values.get("marital_status") == MaritalStatus.MARRIED and not v:
            raise ValueError("marriage_date is required when marital_status is Married")
        return v

    @validator("common_law_start_date", always=True)
    def validate_common_law_date(cls, v, values):
        if values.get("marital_status") == MaritalStatus.COMMON_LAW and not v:
            raise ValueError("common_law_start_date is required when marital_status is Common-Law")
        return v

    @validator("separation_date", always=True)
    def validate_separation_date(cls, v, values):
        status = values.get("marital_status")
        if status == MaritalStatus.SEPARATED and not v:
            raise ValueError("separation_date is required when marital_status is Separated")
        if v:
            marriage = values.get("marriage_date")
            common_law = values.get("common_law_start_date")
            if marriage and v < marriage:
                raise ValueError("separation_date cannot be before marriage_date")
            if common_law and v < common_law:
                raise ValueError("separation_date cannot be before common_law_start_date")
        return v

    @validator("divorce_date", always=True)
    def validate_divorce_date(cls, v, values):
        status = values.get("marital_status")
        if status == MaritalStatus.DIVORCED and not v:
            raise ValueError("divorce_date is required when marital_status is Divorced")
        if v:
            marriage = values.get("marriage_date")
            separation = values.get("separation_date")
            if marriage and v < marriage:
                raise ValueError("divorce_date cannot be before marriage_date")
            if separation and v < separation:
                raise ValueError("divorce_date cannot be before separation_date")
        return v

    @validator("date_of_death", always=True)
    def validate_death_date(cls, v, values):
        status = values.get("marital_status")
        if status == MaritalStatus.WIDOWED and not v:
            raise ValueError("date_of_death is required when marital_status is Widowed")
        if v and v > date.today():
            raise ValueError("date_of_death cannot be in the future")
        return v

    @validator("months_lived_together")
    def validate_months_together(cls, v):
        if v is not None and (v < 0 or v > 12):
            raise ValueError("months_lived_together must be between 0 and 12")
        return v

    @validator("reconciliation_date", always=True)
    def validate_reconciliation(cls, v, values):
        if values.get("reconciliation_occurred") and not v:
            raise ValueError("reconciliation_date is required when reconciliation_occurred is True")
        separation = values.get("separation_date")
        if v and separation and v < separation:
            raise ValueError("reconciliation_date cannot be before separation_date")
        return v

    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            date: lambda v: v.isoformat() if v else None
        }
