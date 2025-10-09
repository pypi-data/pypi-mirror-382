from enum import Enum


class UpdateStandardDeploymentRequestType(str, Enum):
    DEDICATED = "DEDICATED"
    HYBRID = "HYBRID"
    STANDARD = "STANDARD"

    def __str__(self) -> str:
        return str(self.value)
