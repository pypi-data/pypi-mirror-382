from enum import Enum


class ClusterType(str, Enum):
    DEDICATED = "DEDICATED"
    HYBRID = "HYBRID"

    def __str__(self) -> str:
        return str(self.value)
