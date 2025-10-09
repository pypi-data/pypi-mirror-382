from enum import Enum


class ManagedDomainStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"

    def __str__(self) -> str:
        return str(self.value)
