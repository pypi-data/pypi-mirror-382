from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, constr, validator

from common.financial.financial_asset_liablilities import AssetsLiabilities
from common.financial.financial_contributions import SupportAndContributions
from common.financial.financial_eligibility_info import EligibilityInfo
from common.financial.financial_expense_info import ExpenseInfo
from common.financial.financial_foreign_income_info import ForeignIncome
from common.financial.financial_income_info import IncomeInfo

class FinancialInfo(BaseModel):
    income_info: IncomeInfo = Field(default_factory=IncomeInfo)
    support_and_contributions: SupportAndContributions = Field(default_factory=SupportAndContributions)
    expense_info: ExpenseInfo = Field(default_factory=ExpenseInfo)
    assets_liabilities: AssetsLiabilities = Field(default_factory=AssetsLiabilities)
    banking_info_id: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    foreign_income: ForeignIncome = Field(default_factory=ForeignIncome)
    eligibility_info: EligibilityInfo = Field(default_factory=EligibilityInfo)
    last_modified_by: constr(strip_whitespace=True, min_length=1, max_length=255)  # type: ignore
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    financial_notes: Optional[constr(strip_whitespace=True, max_length=1000)] = None  # type: ignore

    # ---------------- Validators ---------------- #
    
    @validator("financial_notes")
    def validate_financial_notes(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError("financial_notes cannot be empty if provided")
        return v

    @validator("income_info", always=True)
    def validate_income_info(cls, v):
        total_income = (
            v.employment_income + v.self_employment_income + v.investment_income +
            v.rental_income + v.pension_income + v.social_assistance_income + v.other_income
        )
        if round(total_income, 2) != round(v.net_income, 2):
            raise ValueError("Sum of income sources must equal net_income")
        return v

    @validator("foreign_income", always=True)
    def validate_foreign_income_info(cls, v):
        if v.has_foreign_income:
            if v.foreign_income_amount is None or v.foreign_income_amount <= 0:
                raise ValueError("foreign_income_amount must be > 0 when has_foreign_income is True")
            if not v.foreign_country:
                raise ValueError("foreign_country is required when has_foreign_income is True")
        return v

    @validator("eligibility_info", always=True)
    def validate_eligibility_info(cls, v, values):
        income = getattr(values.get("income_info"), "net_income", None)
        if v.eligible_for_disability_amount and (income is None or income == 0):
            raise ValueError("Cannot claim disability amount without net income")
        return v

    @validator("support_and_contributions", always=True)
    def validate_support_payments(cls, v):
        if (v.child_support_paid and v.child_support_received and 
            v.child_support_paid > v.child_support_received):
            raise ValueError("child_support_paid cannot exceed child_support_received")
        if (v.spousal_support_paid and v.spousal_support_received and 
            v.spousal_support_paid > v.spousal_support_received):
            raise ValueError("spousal_support_paid cannot exceed spousal_support_received")
        return v

    @validator("assets_liabilities", always=True)
    def validate_assets_vs_liabilities(cls, v):
        if v.total_liabilities and v.total_assets and v.total_liabilities > v.total_assets:
            raise ValueError("total_liabilities cannot exceed total_assets")
        return v

    @validator("expense_info", always=True)
    def validate_expense_info(cls, v, values):
        income = getattr(values.get("income_info"), "net_income", None)
        total_expenses = v.moving_expenses + v.child_care_expenses + v.employment_expenses
        if income is not None and total_expenses > income:
            raise ValueError("Total expenses cannot exceed net income")
        return v

    @validator("last_modified_by")
    def validate_last_modified_by(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("last_modified_by cannot be empty")
        return v

    @validator("last_modified_at")
    def validate_last_modified_at(cls, v):
        if v > datetime.now(timezone.utc):
            raise ValueError("last_modified_at cannot be in the future")
        return v
