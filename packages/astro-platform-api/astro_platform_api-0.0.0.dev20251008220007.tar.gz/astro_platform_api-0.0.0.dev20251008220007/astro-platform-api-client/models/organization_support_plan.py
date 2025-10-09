from enum import Enum


class OrganizationSupportPlan(str, Enum):
    BASIC = "BASIC"
    BASIC_PAYGO = "BASIC_PAYGO"
    BUSINESS = "BUSINESS"
    BUSINESS_CRITICAL = "BUSINESS_CRITICAL"
    BUSINESS_V2 = "BUSINESS_V2"
    DEVELOPER = "DEVELOPER"
    DEVELOPER_PAYGO = "DEVELOPER_PAYGO"
    ENTERPRISE = "ENTERPRISE"
    ENTERPRISE_V2 = "ENTERPRISE_V2"
    INACTIVE = "INACTIVE"
    INTERNAL = "INTERNAL"
    POV = "POV"
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"
    TEAM = "TEAM"
    TEAM_PAYGO = "TEAM_PAYGO"
    TEAM_V2 = "TEAM_V2"
    TRIAL = "TRIAL"
    TRIAL_V2 = "TRIAL_V2"

    def __str__(self) -> str:
        return str(self.value)
