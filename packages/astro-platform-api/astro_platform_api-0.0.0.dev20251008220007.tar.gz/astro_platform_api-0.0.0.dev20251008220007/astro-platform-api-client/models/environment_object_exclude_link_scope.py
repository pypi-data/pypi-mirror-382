from enum import Enum


class EnvironmentObjectExcludeLinkScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
