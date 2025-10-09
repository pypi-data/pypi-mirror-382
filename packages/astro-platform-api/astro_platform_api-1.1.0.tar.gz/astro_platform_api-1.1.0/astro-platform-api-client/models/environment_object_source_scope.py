from enum import Enum


class EnvironmentObjectSourceScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
