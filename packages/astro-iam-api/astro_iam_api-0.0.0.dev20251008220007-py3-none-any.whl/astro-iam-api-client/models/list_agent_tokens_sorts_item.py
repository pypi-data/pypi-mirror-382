from enum import Enum


class ListAgentTokensSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    CREATEDBYIDASC = "createdById:asc"
    CREATEDBYIDDESC = "createdById:desc"
    DESCRIPTIONASC = "description:asc"
    DESCRIPTIONDESC = "description:desc"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"
    TOKENSTARTATASC = "tokenStartAt:asc"
    TOKENSTARTATDESC = "tokenStartAt:desc"
    UPDATEDATASC = "updatedAt:asc"
    UPDATEDATDESC = "updatedAt:desc"
    UPDATEDBYIDASC = "updatedById:asc"
    UPDATEDBYIDDESC = "updatedById:desc"

    def __str__(self) -> str:
        return str(self.value)
