# --- Enums ---
from enum import Enum

class DisabilityStatus(str, Enum):
    NONE = "None"
    APPROVED_DTC = "Approved DTC"
    PENDING_DTC = "Pending DTC"
    SEVERE_PROLONGED = "Severe and Prolonged"
    PARTIAL_DISABILITY = "Partial Disability"
    TEMPORARY_DISABILITY = "Temporary Disability"
