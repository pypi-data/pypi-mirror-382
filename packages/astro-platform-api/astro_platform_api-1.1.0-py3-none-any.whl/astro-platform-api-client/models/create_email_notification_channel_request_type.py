from enum import Enum


class CreateEmailNotificationChannelRequestType(str, Enum):
    DAG_TRIGGER = "DAG_TRIGGER"
    EMAIL = "EMAIL"
    OPSGENIE = "OPSGENIE"
    PAGERDUTY = "PAGERDUTY"
    SLACK = "SLACK"

    def __str__(self) -> str:
        return str(self.value)
