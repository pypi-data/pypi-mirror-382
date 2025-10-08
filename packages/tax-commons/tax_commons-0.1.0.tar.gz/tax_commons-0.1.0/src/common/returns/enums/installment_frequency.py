from enum import Enum

class InstallmentFrequency(str, Enum):
    NOT_REQUIRED = "Not Required"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    ANNUAL = "Annual"

