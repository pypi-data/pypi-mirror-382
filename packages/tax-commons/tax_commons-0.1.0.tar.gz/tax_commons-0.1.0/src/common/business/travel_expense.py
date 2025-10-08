from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum

class TravelExpenseDetails(BaseModel):
    """Business travel expenses"""
    departure_date: date = Field(..., description="Travel start date")
    return_date: date = Field(..., description="Travel end date")
    destination: str = Field(..., description="Travel destination")
    destination_country: Optional[str] = Field(None, description="Destination country")
    
    business_purpose: str = Field(..., description="Purpose of business travel")
    total_days: int = Field(..., ge=1, description="Total days of travel")
    business_days: int = Field(..., ge=1, description="Days spent on business activities")
    personal_days: Optional[int] = Field(None, ge=0, description="Personal days (non-deductible)")
    
    # Expense breakdown
    accommodation: Optional[float] = Field(None, ge=0, description="Hotel/lodging costs")
    transportation: Optional[float] = Field(None, ge=0, description="Airfare, train, etc.")
    ground_transport: Optional[float] = Field(None, ge=0, description="Taxi, car rental, public transit")
    meals: Optional[float] = Field(None, ge=0, description="Meal costs")
    other_expenses: Optional[float] = Field(None, ge=0, description="Other travel-related expenses")
    
    # Per diem
    using_per_diem: bool = Field(False, description="Using per diem rates")
    per_diem_rate: Optional[float] = Field(None, description="Daily per diem rate")