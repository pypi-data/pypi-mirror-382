from enum import Enum


class CreateSlackNotificationChannelRequestEntityType(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    ORGANIZATION = "ORGANIZATION"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
