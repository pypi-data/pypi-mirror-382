from enum import Enum

class RefundMethod(str, Enum):
    DIRECT_DEPOSIT = "Direct Deposit"
    CHEQUE = "Cheque"
    APPLIED_TO_NEXT_YEAR = "Applied to Next Year"
