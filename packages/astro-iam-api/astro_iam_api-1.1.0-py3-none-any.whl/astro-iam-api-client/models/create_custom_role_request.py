from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_custom_role_request_scope_type import CreateCustomRoleRequestScopeType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateCustomRoleRequest")


@_attrs_define
class CreateCustomRoleRequest:
    """
    Attributes:
        name (str): The role's name. Example: Deployment_Viewer.
        permissions (list[str]): The permissions included in the role. Example: ['deployment.get'].
        scope_type (CreateCustomRoleRequestScopeType): The scope of the role. Example: DEPLOYMENT.
        description (Union[Unset, str]): The role's description. Example: Subject can only view deployments..
        restricted_workspace_ids (Union[Unset, list[str]]): The IDs of the Workspaces that the role is restricted to.
            Example: ['cldbvzoi20182g8odxt8ehi5i'].
    """

    name: str
    permissions: list[str]
    scope_type: CreateCustomRoleRequestScopeType
    description: Union[Unset, str] = UNSET
    restricted_workspace_ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        permissions = self.permissions

        scope_type = self.scope_type.value

        description = self.description

        restricted_workspace_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.restricted_workspace_ids, Unset):
            restricted_workspace_ids = self.restricted_workspace_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "permissions": permissions,
                "scopeType": scope_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if restricted_workspace_ids is not UNSET:
            field_dict["restrictedWorkspaceIds"] = restricted_workspace_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        permissions = cast(list[str], d.pop("permissions"))

        scope_type = CreateCustomRoleRequestScopeType(d.pop("scopeType"))

        description = d.pop("description", UNSET)

        restricted_workspace_ids = cast(list[str], d.pop("restrictedWorkspaceIds", UNSET))

        create_custom_role_request = cls(
            name=name,
            permissions=permissions,
            scope_type=scope_type,
            description=description,
            restricted_workspace_ids=restricted_workspace_ids,
        )

        create_custom_role_request.additional_properties = d
        return create_custom_role_request

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
