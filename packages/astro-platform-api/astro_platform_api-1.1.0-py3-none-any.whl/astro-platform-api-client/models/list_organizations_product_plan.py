from enum import Enum


class ListOrganizationsProductPlan(str, Enum):
    BASIC = "BASIC"
    BUSINESS_CRITICAL = "BUSINESS_CRITICAL"
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"
    TRIAL = "TRIAL"

    def __str__(self) -> str:
        return str(self.value)
