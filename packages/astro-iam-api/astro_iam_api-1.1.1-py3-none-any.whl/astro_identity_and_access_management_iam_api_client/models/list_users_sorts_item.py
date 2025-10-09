from enum import Enum


class ListUsersSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    FULLNAMEASC = "fullName:asc"
    FULLNAMEDESC = "fullName:desc"
    IDASC = "id:asc"
    IDDESC = "id:desc"
    UPDATEDATASC = "updatedAt:asc"
    UPDATEDATDESC = "updatedAt:desc"
    USERNAMEASC = "username:asc"
    USERNAMEDESC = "username:desc"

    def __str__(self) -> str:
        return str(self.value)
