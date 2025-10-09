from enum import Enum


class CreateEnvironmentObjectLinkRequestScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
