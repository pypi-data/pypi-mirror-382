from enum import Enum

class ResidencyStatusType(str, Enum):
    CANADIAN_RESIDENT = "Canadian Resident"
    NON_RESIDENT = "Non-Resident"
    DEEMED_RESIDENT = "Deemed Resident"
    DEEMED_NON_RESIDENT = "Deemed Non-Resident"
    PART_YEAR_RESIDENT = "Part-Year Resident"
    FACTUAL_RESIDENT = "Factual Resident"