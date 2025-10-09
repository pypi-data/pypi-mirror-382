from enum import Enum


class RoleTemplateScopeType(str, Enum):
    DEPLOYMENT = "DEPLOYMENT"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    WORKSPACE = "WORKSPACE"

    def __str__(self) -> str:
        return str(self.value)
