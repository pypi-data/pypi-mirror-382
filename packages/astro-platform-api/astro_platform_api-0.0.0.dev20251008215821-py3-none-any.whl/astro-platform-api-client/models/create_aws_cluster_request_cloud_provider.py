from enum import Enum


class CreateAwsClusterRequestCloudProvider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"

    def __str__(self) -> str:
        return str(self.value)
