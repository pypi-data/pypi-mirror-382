# ==================== Enums ====================
from enum import Enum


class FilingStatus(str, Enum):
    """Canadian tax filing status"""
    SINGLE = "Single"
    MARRIED = "Married"
    COMMON_LAW = "Common-Law"
    SEPARATED = "Separated"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
