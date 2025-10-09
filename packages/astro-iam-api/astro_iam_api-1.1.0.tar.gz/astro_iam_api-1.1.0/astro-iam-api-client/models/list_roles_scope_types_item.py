from enum import Enum


class ListRolesScopeTypesItem(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    ORGANIZATION = "ORGANIZATION"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
