from enum import Enum


class GetClusterOptionsProvider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"

    def __str__(self) -> str:
        return str(self.value)
