from enum import Enum

class ReturnStatus(str, Enum):
    NOT_FILED = "Not Filed"
    IN_PROGRESS = "In Progress"
    FILED = "Filed"
    ASSESSED = "Assessed"
    REASSESSED = "Reassessed"
    UNDER_REVIEW = "Under Review"
    OBJECTION_FILED = "Objection Filed"