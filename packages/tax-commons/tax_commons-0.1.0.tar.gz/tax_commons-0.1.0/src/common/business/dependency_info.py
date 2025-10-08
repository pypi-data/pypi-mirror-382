from typing import Optional
from pydantic import BaseModel, Field, validator

from common.tax_payer.enums.dependency_status import DependencyStatus

class DependencyInfo(BaseModel):
    dependency_status: Optional[DependencyStatus] = None
    number_of_dependents: int = Field(default=0, ge=0)
    claimed_as_dependent_by: Optional[str] = None

    @validator("claimed_as_dependent_by", always=True)
    def validate_claimed(cls, v, values):
        if values.get("dependency_status") == DependencyStatus.DEPENDENT and not v:
            raise ValueError("Must specify who claims the taxpayer as dependent")
        return v