from datetime import date, datetime
from typing import Optional
from pydantic import Field, confloat


from common.financial.financial_income_info import IncomeInfo
from common.returns.enums.assessment_status import AssessmentStatus
from common.returns.deduction_info import DeductionInfo

from common.returns.enums.installment_frequency import InstallmentFrequency

from common.tax_payer.enums.filing_status import FilingStatus

# --- Top-Level Tax Info ---
class TaxInfo(IncomeInfo, DeductionInfo):
    tax_filing_status: Optional[FilingStatus] = None
    tax_debt_amount: confloat(ge=0) = Field(default=0.0) # type: ignore
    last_year_filed: Optional[int] = Field(default=None     , ge=1900, le=datetime.now().year)
    expects_refund: bool = Field(default=False)
    expects_amount: Optional[confloat(ge=0)] = Field(default=None) # type: ignore       
    assessment_status: AssessmentStatus = Field(default=AssessmentStatus.NOT_ASSESSED)
    installment_frequency: InstallmentFrequency = Field(default=InstallmentFrequency.NOT_REQUIRED)
    installment_amount: Optional[confloat(ge=0)] = None  # type: ignore
    next_installment_due_date: Optional[date] = None
    
