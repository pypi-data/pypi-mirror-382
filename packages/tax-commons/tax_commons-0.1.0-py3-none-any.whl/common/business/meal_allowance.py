
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum

class MealEntertainmentDetails(BaseModel):
    """Meals and entertainment expenses"""
    location: Optional[str] = Field(None, description="Restaurant or venue name and location")
    business_purpose: str = Field(..., description="Business purpose of meal/entertainment")
    attendees: List[str] = Field(..., min_length=1, description="Names and roles of attendees")
    business_relationship: Optional[str] = Field(None, description="Relationship (client, supplier, employee, etc.)")
    topics_discussed: Optional[str] = Field(None, description="Business topics discussed")
    client_company: Optional[str] = Field(None, description="Client or prospect company name")
    
    # Deduction percentage (varies by country: 50% US/Canada, 100% some countries, etc.)
    deduction_percentage: float = Field(50.0, ge=0, le=100, description="Deduction percentage per tax rules")
    full_deduction_reason: Optional[str] = Field(None, description="Reason if 100% deductible")