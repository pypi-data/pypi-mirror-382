from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum

class OperatingExpenses(BaseModel):
    """Detailed operating expenses for the business"""
    advertising_promotion: float = Field(0, description="Advertising and business promotion")
    meals_entertainment: float = Field(0, description="Meals and entertainment")
    bad_debts: float = Field(0, description="Bad debts")
    insurance: float = Field(0, description="Insurance")
    interest_bank_charges: float = Field(0, description="Interest and bank charges")
    subscriptions_dues: float = Field(0, description="Subscriptions and dues")
    office_expenses: float = Field(0, description="Office expenses")
    office_supplies: float = Field(0, description="Office stationery and supplies")
    professional_fees: float = Field(0, description="Professional fees")
    management_fees: float = Field(0, description="Management and administration fees")
    rent: float = Field(0, description="Rent")
    repairs_maintenance: float = Field(0, description="Repairs and maintenance")
    salaries_wages: float = Field(0, description="Salaries and wages")
    commissions_bonuses: float = Field(0, description="Commissions, allowances, bonuses")
    property_taxes: float = Field(0, description="Property taxes")
    travel: float = Field(0, description="Travel expenses")
    utilities_light_heat_water: float = Field(0, description="Utilities - light, heat, water")
    utilities_telephone: float = Field(0, description="Utilities - telephone")
    fuel_costs: float = Field(0, description="Fuel costs (excluding vehicle)")
    delivery_freight: float = Field(0, description="Delivery, freight, express")
    motor_vehicle: float = Field(0, description="Motor vehicle (see auto tab)")
    motor_vehicle_other: float = Field(0, description="Motor vehicle - other")
    capital_cost_allowance: float = Field(0, description="Capital cost allowance (see fixed assets tab)")
    other_expenses: float = Field(0, description="Other operating expenses")
    business_use_of_home: float = Field(0, description="Business-use-of-home (see home office tab)")

    def total(self) -> float:
        """Compute total operating expenses"""
        return sum(self.__dict__.values())

