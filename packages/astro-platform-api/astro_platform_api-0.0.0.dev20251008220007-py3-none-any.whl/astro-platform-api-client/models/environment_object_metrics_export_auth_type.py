from enum import Enum


class EnvironmentObjectMetricsExportAuthType(str, Enum):
    AUTH_TOKEN = "AUTH_TOKEN"
    BASIC = "BASIC"

    def __str__(self) -> str:
        return str(self.value)
