from enum import Enum


class ListNotificationChannelsSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"
    UPDATEDATASC = "updatedAt:asc"
    UPDATEDATDESC = "updatedAt:desc"

    def __str__(self) -> str:
        return str(self.value)
