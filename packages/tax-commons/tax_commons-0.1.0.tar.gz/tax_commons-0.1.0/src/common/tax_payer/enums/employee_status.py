from enum import Enum

class EmploymentStatus(str, Enum):
    EMPLOYED_FULL_TIME = "Employed Full-Time"
    EMPLOYED_PART_TIME = "Employed Part-Time"
    SELF_EMPLOYED = "Self-Employed"
    UNEMPLOYED = "Unemployed"
    RETIRED = "Retired"
    ON_LEAVE = "On Leave"
    DISABLED = "Disabled"
    STUDENT = "Student"
    HOMEMAKER = "Homemaker"
    SEASONAL = "Seasonal Worker"
