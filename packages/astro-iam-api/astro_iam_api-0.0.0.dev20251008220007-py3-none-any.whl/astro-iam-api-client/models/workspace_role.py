from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.workspace_role_role import WorkspaceRoleRole

T = TypeVar("T", bound="WorkspaceRole")


@_attrs_define
class WorkspaceRole:
    """
    Attributes:
        role (WorkspaceRoleRole): The role of the subject in the Workspace. Example: WORKSPACE_MEMBER.
        workspace_id (str): The Workspace ID. Example: clm8t5u4q000008jq4qoc3036.
    """

    role: WorkspaceRoleRole
    workspace_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "workspaceId": workspace_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = WorkspaceRoleRole(d.pop("role"))

        workspace_id = d.pop("workspaceId")

        workspace_role = cls(
            role=role,
            workspace_id=workspace_id,
        )

        workspace_role.additional_properties = d
        return workspace_role

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
