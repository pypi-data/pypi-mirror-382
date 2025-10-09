from enum import Enum


class EnvironmentObjectLinkScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
