from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum

class HomeOfficeDetails(BaseModel):
    """Home office expenses"""
    workspace_area: float = Field(..., gt=0, description="Area of workspace (sq ft or sq m)")
    total_home_area: float = Field(..., gt=0, description="Total home area (sq ft or sq m)")
    area_unit: str = Field("sq_ft", description="Unit of measurement (sq_ft or sq_m)")
    workspace_percentage: Optional[float] = Field(None, ge=0, le=100, description="Calculated workspace percentage")
    
    # Qualification criteria
    exclusive_use: bool = Field(False, description="Used exclusively for business")
    regular_use: bool = Field(False, description="Used regularly for business")
    principal_place: bool = Field(False, description="Principal place of business")
    client_meetings: bool = Field(False, description="Used to meet clients/customers")
    
    # Deductible expenses
    rent: Optional[float] = Field(None, ge=0, description="Rent portion")
    mortgage_interest: Optional[float] = Field(None, ge=0, description="Mortgage interest portion")
    property_taxes: Optional[float] = Field(None, ge=0, description="Property taxes portion")
    insurance: Optional[float] = Field(None, ge=0, description="Insurance portion")
    utilities: Optional[float] = Field(None, ge=0, description="Utilities portion")
    repairs_maintenance: Optional[float] = Field(None, ge=0, description="Repairs and maintenance portion")
    depreciation: Optional[float] = Field(None, ge=0, description="Depreciation portion")