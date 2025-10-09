from enum import Enum


class CreateDedicatedDeploymentRequestType(str, Enum):
    DEDICATED = "DEDICATED"
    HYBRID = "HYBRID"
    STANDARD = "STANDARD"

    def __str__(self) -> str:
        return str(self.value)
