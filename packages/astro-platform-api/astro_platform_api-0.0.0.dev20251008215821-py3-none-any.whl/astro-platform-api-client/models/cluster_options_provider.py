from enum import Enum


class ClusterOptionsProvider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"

    def __str__(self) -> str:
        return str(self.value)
