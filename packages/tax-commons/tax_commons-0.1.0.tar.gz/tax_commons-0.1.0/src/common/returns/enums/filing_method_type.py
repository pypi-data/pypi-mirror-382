# --- Enums ---
from enum import Enum


class FilingMethodType(str, Enum):
    EFILE = "EFILE"
    NETFILE = "NETFILE"
    PAPER = "Paper"
    AUTO_FILL = "Auto-fill my return"
    REPRESENT_A_CLIENT = "Represent a Client"
