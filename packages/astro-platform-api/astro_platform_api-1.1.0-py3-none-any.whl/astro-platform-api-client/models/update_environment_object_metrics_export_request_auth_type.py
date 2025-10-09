from enum import Enum


class UpdateEnvironmentObjectMetricsExportRequestAuthType(str, Enum):
    AUTH_TOKEN = "AUTH_TOKEN"
    BASIC = "BASIC"

    def __str__(self) -> str:
        return str(self.value)
