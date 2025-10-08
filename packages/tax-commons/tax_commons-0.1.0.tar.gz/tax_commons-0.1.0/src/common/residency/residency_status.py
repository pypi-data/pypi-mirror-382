from enum import Enum


class ResidencyStatus(str, Enum):
    """Canadian residency status for tax purposes"""
    RESIDENT = "Resident"
    NON_RESIDENT = "Non-Resident"
    DEEMED_RESIDENT = "Deemed Resident"
    DEEMED_NON_RESIDENT = "Deemed Non-Resident"
    EMIGRANT = "Emigrant"
    IMMIGRANT = "Immigrant"
    PART_YEAR_RESIDENT = "Part-Year Resident"
    FACTUAL_RESIDENT = "Factual Resident"
