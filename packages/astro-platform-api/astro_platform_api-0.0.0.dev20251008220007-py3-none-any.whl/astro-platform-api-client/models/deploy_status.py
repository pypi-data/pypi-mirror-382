from enum import Enum


class DeployStatus(str, Enum):
    DEPLOYED = "DEPLOYED"
    FAILED = "FAILED"
    INITIALIZED = "INITIALIZED"

    def __str__(self) -> str:
        return str(self.value)
