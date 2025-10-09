from enum import Enum


class DefaultRoleScopeType(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
