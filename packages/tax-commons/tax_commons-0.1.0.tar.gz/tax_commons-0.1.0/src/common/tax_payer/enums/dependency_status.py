from enum import Enum

class DependencyStatus(str, Enum):
    INDEPENDENT = "Independent"
    DEPENDENT = "Dependent"
    ELIGIBLE_DEPENDANT = "Eligible Dependant"
    INFIRM_DEPENDANT = "Infirm Dependant"