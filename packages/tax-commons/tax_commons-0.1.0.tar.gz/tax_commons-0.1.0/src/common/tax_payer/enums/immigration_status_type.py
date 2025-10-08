from enum import Enum

class ImmigrationStatusType(str, Enum):
    CITIZEN = "Canadian Citizen"
    PERMANENT_RESIDENT = "Permanent Resident"
    WORK_PERMIT = "Work Permit Holder"
    STUDY_PERMIT = "Study Permit Holder"
    VISITOR = "Visitor"
    REFUGEE = "Refugee/Protected Person"
    TEMPORARY_RESIDENT = "Temporary Resident"