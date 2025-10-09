from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_user_roles_request_organization_role import UpdateUserRolesRequestOrganizationRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_role import DeploymentRole
    from ..models.workspace_role import WorkspaceRole


T = TypeVar("T", bound="UpdateUserRolesRequest")


@_attrs_define
class UpdateUserRolesRequest:
    """
    Attributes:
        deployment_roles (Union[Unset, list['DeploymentRole']]): The user's updated Deployment roles. Requires also
            specifying an `OrganizationRole`.
        organization_role (Union[Unset, UpdateUserRolesRequestOrganizationRole]): The user's updated Organization role.
            Example: ORGANIZATION_MEMBER.
        workspace_roles (Union[Unset, list['WorkspaceRole']]): The user's updated Workspace roles. Requires also
            specifying an `OrganizationRole`.
    """

    deployment_roles: Union[Unset, list["DeploymentRole"]] = UNSET
    organization_role: Union[Unset, UpdateUserRolesRequestOrganizationRole] = UNSET
    workspace_roles: Union[Unset, list["WorkspaceRole"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deployment_roles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.deployment_roles, Unset):
            deployment_roles = []
            for deployment_roles_item_data in self.deployment_roles:
                deployment_roles_item = deployment_roles_item_data.to_dict()
                deployment_roles.append(deployment_roles_item)

        organization_role: Union[Unset, str] = UNSET
        if not isinstance(self.organization_role, Unset):
            organization_role = self.organization_role.value

        workspace_roles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.workspace_roles, Unset):
            workspace_roles = []
            for workspace_roles_item_data in self.workspace_roles:
                workspace_roles_item = workspace_roles_item_data.to_dict()
                workspace_roles.append(workspace_roles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if deployment_roles is not UNSET:
            field_dict["deploymentRoles"] = deployment_roles
        if organization_role is not UNSET:
            field_dict["organizationRole"] = organization_role
        if workspace_roles is not UNSET:
            field_dict["workspaceRoles"] = workspace_roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deployment_role import DeploymentRole
        from ..models.workspace_role import WorkspaceRole

        d = dict(src_dict)
        deployment_roles = []
        _deployment_roles = d.pop("deploymentRoles", UNSET)
        for deployment_roles_item_data in _deployment_roles or []:
            deployment_roles_item = DeploymentRole.from_dict(deployment_roles_item_data)

            deployment_roles.append(deployment_roles_item)

        _organization_role = d.pop("organizationRole", UNSET)
        organization_role: Union[Unset, UpdateUserRolesRequestOrganizationRole]
        if isinstance(_organization_role, Unset):
            organization_role = UNSET
        else:
            organization_role = UpdateUserRolesRequestOrganizationRole(_organization_role)

        workspace_roles = []
        _workspace_roles = d.pop("workspaceRoles", UNSET)
        for workspace_roles_item_data in _workspace_roles or []:
            workspace_roles_item = WorkspaceRole.from_dict(workspace_roles_item_data)

            workspace_roles.append(workspace_roles_item)

        update_user_roles_request = cls(
            deployment_roles=deployment_roles,
            organization_role=organization_role,
            workspace_roles=workspace_roles,
        )

        update_user_roles_request.additional_properties = d
        return update_user_roles_request

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
