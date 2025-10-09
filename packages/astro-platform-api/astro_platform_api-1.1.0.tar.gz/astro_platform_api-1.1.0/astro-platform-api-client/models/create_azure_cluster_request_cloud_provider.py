from enum import Enum


class CreateAzureClusterRequestCloudProvider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"

    def __str__(self) -> str:
        return str(self.value)
