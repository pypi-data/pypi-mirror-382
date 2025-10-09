from enum import Enum


class ListTeamsSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    DESCRIPTIONASC = "description:asc"
    DESCRIPTIONDESC = "description:desc"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"
    UPDATEDATASC = "updatedAt:asc"
    UPDATEDATDESC = "updatedAt:desc"

    def __str__(self) -> str:
        return str(self.value)
