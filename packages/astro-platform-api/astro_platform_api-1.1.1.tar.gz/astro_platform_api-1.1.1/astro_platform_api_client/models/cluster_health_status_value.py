from enum import Enum


class ClusterHealthStatusValue(str, Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
