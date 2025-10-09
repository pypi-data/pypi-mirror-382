from enum import Enum


class ListOrganizationsAstronomerProduct(str, Enum):
    ASTRO = "ASTRO"
    OBSERVE = "OBSERVE"

    def __str__(self) -> str:
        return str(self.value)
