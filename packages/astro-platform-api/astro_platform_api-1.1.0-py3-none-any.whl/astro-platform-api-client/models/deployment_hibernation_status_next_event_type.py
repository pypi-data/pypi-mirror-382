from enum import Enum


class DeploymentHibernationStatusNextEventType(str, Enum):
    HIBERNATE = "HIBERNATE"
    WAKE = "WAKE"

    def __str__(self) -> str:
        return str(self.value)
