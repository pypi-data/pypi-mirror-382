from enum import Enum


class UpdateDedicatedClusterRequestClusterType(str, Enum):
    DEDICATED = "DEDICATED"

    def __str__(self) -> str:
        return str(self.value)
