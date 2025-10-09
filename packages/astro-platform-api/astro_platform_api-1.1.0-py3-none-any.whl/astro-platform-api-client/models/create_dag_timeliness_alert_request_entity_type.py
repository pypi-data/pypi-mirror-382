from enum import Enum


class CreateDagTimelinessAlertRequestEntityType(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"

    def __str__(self) -> str:
        return str(self.value)
