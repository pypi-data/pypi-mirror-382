from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, constr, validator

# ==== External imports (assumed in your project) ====
from common.dependent.spouse.dependent_marital_status import MaritalStatusDetails
from common.education.education_info import EducationInfo
from common.financial.financial_info import FinancialInfo
from common.info.identification_info import IdentificationInfo
from common.info.tax_info import TaxInfo
from common.medical.medical_info import MedicalInfo
from common.residency.residency_immigration_info import ImmigrationInfo
from common.info.contact_info import ContactInfo
from common.info.personal_info import PersonalInfo
from common.education.status_info import AuditInfo, EmploymentInfo
from common.info.address_info import Address

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


# ==================== Support Payments ====================
class SpouseSupportPayments(BaseModel):
    spousal_support_paid: Optional[float] = Field(default=None, ge=0)
    spousal_support_received: Optional[float] = Field(default=None, ge=0)
    child_support_paid: Optional[float] = Field(default=None, ge=0)
    child_support_received: Optional[float] = Field(default=None, ge=0)

    @validator("spousal_support_paid", "spousal_support_received",
               "child_support_paid", "child_support_received", pre=True)
    def validate_support_amounts(cls, v):
        if v is None:
            return None
        v = round(float(v), 2)
        if v > 10_000_000:
            raise ValueError("Support amount exceeds maximum reasonable value")
        return v


# ==================== Serialization Helper ====================
def serialize_spouse_info(spouse_info: Dict[str, Any]) -> Dict[str, Any]:
    if "_id" in spouse_info:
        spouse_info["id"] = str(spouse_info["_id"]) if isinstance(spouse_info["_id"], ObjectId) else spouse_info["_id"]
        del spouse_info["_id"]
    return jsonable_encoder(spouse_info)


# ==================== Additional Info ====================
class SpouseAdditionalInfo(BaseModel):
    primary_language: Optional[str] = Field(default=None, min_length=1, max_length=50)
    requires_translator: Optional[bool] = None
    spouse_notes: Optional[str] = Field(default=None, max_length=1000)


# ==================== Main Spouse Info ====================
class SpouseInfo(BaseModel):
    """Complete spouse information with all components"""

    dependent_id: constr(strip_whitespace=True, min_length=1, max_length=50)  # type: ignore
    identification: IdentificationInfo

    personal_info: Optional[PersonalInfo] = None
    spouse_info: Optional[MaritalStatusDetails] = None
    contact_info: Optional[ContactInfo] = None
    address_info: Optional[Address] = None
    immigration_residency: Optional[ImmigrationInfo] = None
    employment_info: Optional[EmploymentInfo] = None
    financial_info: Optional[FinancialInfo] = None
    education_info: Optional[EducationInfo] = None
    health_info: Optional[MedicalInfo] = None
    emergency_contact: Optional[ContactInfo] = None
    banking_info_id: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None  # type: ignore
    tax_filing_info: Optional[TaxInfo] = None
    support_payments: Optional[SpouseSupportPayments] = None
    additional_info: Optional[SpouseAdditionalInfo] = None
    audit: Optional[AuditInfo] = None

    # ---------------- Validators ---------------- #
    @validator("dependent_id")
    def validate_dependent_id(cls, v):
        if not v.strip():
            raise ValueError("dependent_id cannot be empty")
        return v

    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
        }
        schema_extra = {
            "example": {
                "dependent_id": "DEP-001",
                "identification": {"taxpayer_id": "TAX-001", "spouse_id": "SPO-001"},
                "personal_info": {"first_name": "Jane", "last_name": "Doe", "date_of_birth": "1985-03-15"},
                "spouse_info": {
                    "marital_status": "Married",
                    "marriage_date": "2010-06-20",
                    "lived_together_all_year": True,
                    "months_lived_together": 12
                },
                "immigration_residency": {"canadian_resident": True},
                "employment_info": {"employment_status": "Employed Full-Time"},
                "financial_info": {"net_income": 50000.00},
                "tax_filing_info": {"files_separate_tax_return": True},
                "address_info": {"same_address_as_taxpayer": True, "country": "Canada"},
                "additional_info": {"primary_language": "English"},
                "audit": {
                    "created_by": "system",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_modified_by": "system",
                    "last_modified_at": "2024-01-01T00:00:00Z"
                }
            }
        }
