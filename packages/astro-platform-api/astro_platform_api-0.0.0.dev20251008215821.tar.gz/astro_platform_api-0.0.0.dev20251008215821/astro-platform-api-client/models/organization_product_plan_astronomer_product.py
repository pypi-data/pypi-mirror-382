from enum import Enum


class OrganizationProductPlanAstronomerProduct(str, Enum):
    ASTRO_OBSERVE = "ASTRO OBSERVE"

    def __str__(self) -> str:
        return str(self.value)
