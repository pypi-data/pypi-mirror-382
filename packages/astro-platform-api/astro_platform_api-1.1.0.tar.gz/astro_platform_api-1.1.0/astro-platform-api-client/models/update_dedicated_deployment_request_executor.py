from enum import Enum


class UpdateDedicatedDeploymentRequestExecutor(str, Enum):
    ASTRO = "ASTRO"
    CELERY = "CELERY"
    KUBERNETES = "KUBERNETES"

    def __str__(self) -> str:
        return str(self.value)
