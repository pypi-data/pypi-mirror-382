from enum import Enum


class UpdateHybridDeploymentRequestExecutor(str, Enum):
    CELERY = "CELERY"
    KUBERNETES = "KUBERNETES"

    def __str__(self) -> str:
        return str(self.value)
