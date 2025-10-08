from enum import Enum


class ServiceTier(str, Enum):
    info = "info"
    STANDARD = "Standard"
    PREMIUM = "Premium"
    VIP = "VIP"
