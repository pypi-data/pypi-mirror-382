from enum import Enum


class CreateGcpClusterRequestType(str, Enum):
    DEDICATED = "DEDICATED"
    HYBRID = "HYBRID"

    def __str__(self) -> str:
        return str(self.value)
