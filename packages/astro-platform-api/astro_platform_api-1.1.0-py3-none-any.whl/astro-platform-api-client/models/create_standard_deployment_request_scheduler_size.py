from enum import Enum


class CreateStandardDeploymentRequestSchedulerSize(str, Enum):
    EXTRA_LARGE = "EXTRA_LARGE"
    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"

    def __str__(self) -> str:
        return str(self.value)
