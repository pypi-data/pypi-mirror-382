import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.user_organization_role import UserOrganizationRole
from ..models.user_status import UserStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_role import DeploymentRole
    from ..models.workspace_role import WorkspaceRole


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        avatar_url (str): The URL for the user's profile image. Example: https://avatar.url.
        created_at (datetime.datetime): The time when the user was created in UTC, formatted as `YYYY-MM-DDTHH:MM:SSZ`.
            Example: 2022-11-22T04:37:12Z.
        full_name (str): The user's full name. Example: Jane Doe.
        id (str): The user's ID. Example: clm9sq6s0000008kz7uvl7yz7.
        status (UserStatus): The user's status. Example: ACTIVE.
        updated_at (datetime.datetime): The time when the user was updated in UTC, formatted as `YYYY-MM-DDTHH:MM:SSZ`.
            Example: 2022-11-22T04:37:12Z.
        username (str): The user's username. Example: user1@company.com.
        deployment_roles (Union[Unset, list['DeploymentRole']]): The user's Deployment roles.
        organization_role (Union[Unset, UserOrganizationRole]): The user's Organization role. Example:
            ORGANIZATION_MEMBER.
        workspace_roles (Union[Unset, list['WorkspaceRole']]): The user's Workspace roles.
    """

    avatar_url: str
    created_at: datetime.datetime
    full_name: str
    id: str
    status: UserStatus
    updated_at: datetime.datetime
    username: str
    deployment_roles: Union[Unset, list["DeploymentRole"]] = UNSET
    organization_role: Union[Unset, UserOrganizationRole] = UNSET
    workspace_roles: Union[Unset, list["WorkspaceRole"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        avatar_url = self.avatar_url

        created_at = self.created_at.isoformat()

        full_name = self.full_name

        id = self.id

        status = self.status.value

        updated_at = self.updated_at.isoformat()

        username = self.username

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
        field_dict.update(
            {
                "avatarUrl": avatar_url,
                "createdAt": created_at,
                "fullName": full_name,
                "id": id,
                "status": status,
                "updatedAt": updated_at,
                "username": username,
            }
        )
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
        avatar_url = d.pop("avatarUrl")

        created_at = isoparse(d.pop("createdAt"))

        full_name = d.pop("fullName")

        id = d.pop("id")

        status = UserStatus(d.pop("status"))

        updated_at = isoparse(d.pop("updatedAt"))

        username = d.pop("username")

        deployment_roles = []
        _deployment_roles = d.pop("deploymentRoles", UNSET)
        for deployment_roles_item_data in _deployment_roles or []:
            deployment_roles_item = DeploymentRole.from_dict(deployment_roles_item_data)

            deployment_roles.append(deployment_roles_item)

        _organization_role = d.pop("organizationRole", UNSET)
        organization_role: Union[Unset, UserOrganizationRole]
        if isinstance(_organization_role, Unset):
            organization_role = UNSET
        else:
            organization_role = UserOrganizationRole(_organization_role)

        workspace_roles = []
        _workspace_roles = d.pop("workspaceRoles", UNSET)
        for workspace_roles_item_data in _workspace_roles or []:
            workspace_roles_item = WorkspaceRole.from_dict(workspace_roles_item_data)

            workspace_roles.append(workspace_roles_item)

        user = cls(
            avatar_url=avatar_url,
            created_at=created_at,
            full_name=full_name,
            id=id,
            status=status,
            updated_at=updated_at,
            username=username,
            deployment_roles=deployment_roles,
            organization_role=organization_role,
            workspace_roles=workspace_roles,
        )

        user.additional_properties = d
        return user

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
