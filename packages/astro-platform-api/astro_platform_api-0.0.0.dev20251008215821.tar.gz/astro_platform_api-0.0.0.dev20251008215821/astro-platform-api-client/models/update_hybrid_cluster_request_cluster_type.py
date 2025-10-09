from enum import Enum


class UpdateHybridClusterRequestClusterType(str, Enum):
    HYBRID = "HYBRID"

    def __str__(self) -> str:
        return str(self.value)
