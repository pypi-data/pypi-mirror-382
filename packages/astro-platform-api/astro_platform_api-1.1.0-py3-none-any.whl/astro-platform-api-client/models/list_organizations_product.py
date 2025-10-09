from enum import Enum


class ListOrganizationsProduct(str, Enum):
    HOSTED = "HOSTED"
    HYBRID = "HYBRID"

    def __str__(self) -> str:
        return str(self.value)
