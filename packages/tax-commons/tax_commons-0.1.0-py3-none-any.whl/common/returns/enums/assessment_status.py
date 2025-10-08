from enum import Enum

class AssessmentStatus(str, Enum):
    NOT_ASSESSED = "Not Assessed"
    ASSESSED = "Assessed"
    REASSESSED = "Reassessed"
    NOTICE_SENT = "Notice Sent"
    BALANCE_DUE = "Balance Due"
    REFUND_ISSUED = "Refund Issued"
    UNDER_OBJECTION = "Under Objection"
