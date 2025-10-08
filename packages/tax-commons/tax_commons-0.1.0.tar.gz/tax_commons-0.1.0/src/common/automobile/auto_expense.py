from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal
from datetime import date

class AutomobileExpense(BaseModel):
    client_name: str = Field(..., description="Name of the client")
    
    # Vehicle Details
    make: str = Field(..., description="Vehicle make")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Year of manufacture")
    acquisition_date: date = Field(..., description="Date of acquisition or lease start")
    disposition_date: Optional[date] = Field(None, description="Date of disposition or lease end, if applicable")
    
    # Expenses
    fuel: Decimal = Field(default=0.0, ge=0, description="Fuel expenses")
    interest: Decimal = Field(default=0.0, ge=0, description="Interest on automobile loan")
    insurance: Decimal = Field(default=0.0, ge=0, description="Insurance costs")
    licenses_and_registration: Decimal = Field(default=0.0, ge=0, description="Licenses and registration fees")
    maintenance_and_repairs: Decimal = Field(default=0.0, ge=0, description="Maintenance and repair costs")
    leasing_costs: Decimal = Field(default=0.0, ge=0, description="Leasing costs")
    other_percentage_business: Decimal = Field(default=0.0, ge=0, description="Other expenses (% business use)")
    other_100_business: Decimal = Field(default=0.0, ge=0, description="Other expenses (100% business use)")
    
    # Tax and HST fields (optional)
    hst_fuel: Optional[Decimal] = Field(default=0.0, ge=0)
    hst_interest: Optional[Decimal] = Field(default=0.0, ge=0)
    hst_insurance: Optional[Decimal] = Field(default=0.0, ge=0)
    
    # Kilometers
    business_kms: Decimal = Field(default=0.0, ge=0, description="Business kilometers driven")
    total_kms: Decimal = Field(default=0.0, ge=0, description="Total kilometers driven")
    
    # Depreciation / UCC
    ucc_beginning: Decimal = Field(default=0.0, ge=0, description="Un-depreciated capital cost at beginning of year")
    additions: Decimal = Field(default=0.0, ge=0, description="Additions to capital cost")
    proceeds: Decimal = Field(default=0.0, ge=0, description="Proceeds from disposition")
    net_additions: Decimal = Field(default=0.0, ge=0, description="Net additions (additions - proceeds)")
    depreciation_rate: Decimal = Field(default=30.0, ge=0, le=100, description="Depreciation rate in %")
    depreciation_amount: Decimal = Field(default=0.0, ge=0, description="Depreciation amount")
    ucc_end: Decimal = Field(default=0.0, ge=0, description="Un-depreciated capital cost at end of year")
    
    @validator("total_kms")
    def check_total_kms(cls, v, values):
        if "business_kms" in values and v < values["business_kms"]:
            raise ValueError("Total kilometers cannot be less than business kilometers")
        return v
    
    @validator("year")
    def validate_year(cls, v):
        if v < 1900 or v > 2100:
            raise ValueError("Year must be realistic")
        return v
