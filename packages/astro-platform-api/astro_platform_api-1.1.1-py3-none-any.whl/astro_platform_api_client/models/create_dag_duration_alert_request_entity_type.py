from enum import Enum


class CreateDagDurationAlertRequestEntityType(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
