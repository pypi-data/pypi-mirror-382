from enum import Enum


class CreateDagSuccessAlertRequestEntityType(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
