from enum import Enum


class DeployType(str, Enum):
    DAG_ONLY = "DAG_ONLY"
    IMAGE_AND_DAG = "IMAGE_AND_DAG"
    IMAGE_ONLY = "IMAGE_ONLY"

    def __str__(self) -> str:
        return str(self.value)
