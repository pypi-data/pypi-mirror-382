from enum import Enum


class OrganizationProduct(str, Enum):
    HOSTED = "HOSTED"
    HYBRID = "HYBRID"

    def __str__(self) -> str:
        return str(self.value)
