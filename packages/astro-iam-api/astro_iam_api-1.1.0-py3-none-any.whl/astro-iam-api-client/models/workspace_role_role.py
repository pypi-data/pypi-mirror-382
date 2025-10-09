from enum import Enum


class WorkspaceRoleRole(str, Enum):
    WORKSPACE_ACCESSOR = "WORKSPACE_ACCESSOR"
    WORKSPACE_AUTHOR = "WORKSPACE_AUTHOR"
    WORKSPACE_MEMBER = "WORKSPACE_MEMBER"
    WORKSPACE_OPERATOR = "WORKSPACE_OPERATOR"
    WORKSPACE_OWNER = "WORKSPACE_OWNER"

    def __str__(self) -> str:
        return str(self.value)
