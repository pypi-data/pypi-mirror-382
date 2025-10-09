from enum import Enum


class CreateDeployRequestType(str, Enum):
    BUNDLE = "BUNDLE"
    DAG_ONLY = "DAG_ONLY"
    IMAGE_AND_DAG = "IMAGE_AND_DAG"
    IMAGE_ONLY = "IMAGE_ONLY"

    def __str__(self) -> str:
        return str(self.value)
