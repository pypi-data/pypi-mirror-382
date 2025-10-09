from enum import Enum


class ListTeamMembersSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    FULLNAMEASC = "fullName:asc"
    FULLNAMEDESC = "fullName:desc"
    USERIDASC = "userId:asc"
    USERIDDESC = "userId:desc"
    USERNAMEASC = "username:asc"
    USERNAMEDESC = "username:desc"

    def __str__(self) -> str:
        return str(self.value)
