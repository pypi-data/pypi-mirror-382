from datetime import datetime, timezone
from pydantic import BaseModel, Field

from common.business.dependency_info import DependencyInfo
from common.financial.bankruptcy_info import BankruptcyInfo
from common.info.tax_info import TaxInfo
from common.medical.medical_disability_info import DisabilityInfo
from common.residency.residency_immigration_info import ImmigrationInfo
from common.residency.residency_info import ResidencyInfo

# --- Aggregator ---
class StatusInfo(BaseModel):
    disability: DisabilityInfo
    tax: TaxInfo
    dependency: DependencyInfo
    residency: ResidencyInfo
    immigration: ImmigrationInfo
    bankruptcy: BankruptcyInfo
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by: str
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



    class Config:
        use_enum_values = True
