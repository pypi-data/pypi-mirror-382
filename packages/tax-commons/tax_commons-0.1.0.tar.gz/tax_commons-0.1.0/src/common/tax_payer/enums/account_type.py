from enum import Enum

class AccountType(str, Enum):
    INDIVIDUAL = "Individual"
    SOLE_PROPRIETOR = "Sole Proprietor"
    TRUST = "Trust"
    ESTATE = "Estate"
    PARTNERSHIP = "Partnership"
    CORPORATION = "Corporation"