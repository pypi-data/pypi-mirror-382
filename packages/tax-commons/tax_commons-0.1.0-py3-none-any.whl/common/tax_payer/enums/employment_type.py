from enum import Enum

class EmploymentType(str, Enum):
    full_time = "Full-Time"
    part_time = "Part-Time"
    contract = "Contract"
    intern = "Intern"
    other = "Other"
