from enum import Enum


class CreateEnvironmentObjectRequestScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
