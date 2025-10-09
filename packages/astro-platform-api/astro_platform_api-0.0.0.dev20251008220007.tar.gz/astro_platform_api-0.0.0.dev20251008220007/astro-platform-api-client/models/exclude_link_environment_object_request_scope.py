from enum import Enum


class ExcludeLinkEnvironmentObjectRequestScope(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
