from enum import Enum


class UpdateEnvironmentObjectLinkRequestScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
