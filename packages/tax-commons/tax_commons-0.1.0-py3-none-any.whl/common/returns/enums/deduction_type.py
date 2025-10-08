from enum import Enum


class DeductionType(str, Enum):
    """Common tax deduction types - extend as needed for your jurisdiction."""
    SECTION_80C = "Section 80C"  # India - Investments, insurance, etc.
    SECTION_80D = "Section 80D"  # India - Medical insurance
    SECTION_80E = "Section 80E"  # India - Education loan interest
    SECTION_80G = "Section 80G"  # India - Charitable donations
    HOME_LOAN_INTEREST = "Home Loan Interest"
    MEDICAL_EXPENSES = "Medical Expenses"
    EDUCATION_EXPENSES = "Education Expenses"
    CHARITABLE_DONATIONS = "Charitable Donations"
    BUSINESS_EXPENSES = "Business Expenses"
    RETIREMENT_CONTRIBUTIONS = "Retirement Contributions"
    DEPENDENT_CARE = "Dependent Care"
    OTHER = "Other"
