from enum import Enum


class TaxpayerStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    DECEASED = "Deceased"
    MERGED = "Merged"
    ARCHIVED = "Archived"