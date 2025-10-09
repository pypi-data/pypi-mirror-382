from enum import Enum


class ListEnvironmentObjectsSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    OBJECTKEYASC = "objectKey:asc"
    OBJECTKEYDESC = "objectKey:desc"
    OBJECTTYPEASC = "objectType:asc"
    OBJECTTYPEDESC = "objectType:desc"
    UPDATEDATASC = "updatedAt:asc"
    UPDATEDATDESC = "updatedAt:desc"

    def __str__(self) -> str:
        return str(self.value)
