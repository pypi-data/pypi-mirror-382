from enum import Enum


class EnvironmentObjectScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
