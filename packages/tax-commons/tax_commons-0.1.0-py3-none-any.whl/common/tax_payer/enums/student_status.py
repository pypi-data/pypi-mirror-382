from enum import Enum

class StudentStatus(str, Enum):
    NOT_STUDENT = "Not a Student"
    PART_TIME = "Part-Time Student"
    FULL_TIME = "Full-Time Student"
    GRADUATE_STUDENT = "Graduate Student"
    POSTDOCTORAL = "Postdoctoral"
    VOCATIONAL_TRAINING = "Vocational Training"