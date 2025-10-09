from enum import Enum


class ListNotificationChannelsEntityType(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    ORGANIZATION = "ORGANIZATION"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
