from enum import Enum


class ListApiTokensSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    DESCRIPTIONASC = "description:asc"
    DESCRIPTIONDESC = "description:desc"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"
    TOKENSTARTATASC = "tokenStartAt:asc"
    TOKENSTARTATDESC = "tokenStartAt:desc"
    UPDATEDATASC = "updatedAt:asc"
    UPDATEDATDESC = "updatedAt:desc"

    def __str__(self) -> str:
        return str(self.value)
