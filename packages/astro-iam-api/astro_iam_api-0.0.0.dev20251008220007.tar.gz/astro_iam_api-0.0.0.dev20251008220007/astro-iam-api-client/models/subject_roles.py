from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.subject_roles_organization_role import SubjectRolesOrganizationRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_role import DeploymentRole
    from ..models.workspace_role import WorkspaceRole


T = TypeVar("T", bound="SubjectRoles")


@_attrs_define
class SubjectRoles:
    """
    Attributes:
        deployment_roles (Union[Unset, list['DeploymentRole']]): A list of the subject's Deployment roles. Currently
            only for API tokens.
        organization_role (Union[Unset, SubjectRolesOrganizationRole]): The subject's Organization role. Example:
            ORGANIZATION_OWNER.
        workspace_roles (Union[Unset, list['WorkspaceRole']]): A list of the subject's Workspace roles.
    """

    deployment_roles: Union[Unset, list["DeploymentRole"]] = UNSET
    organization_role: Union[Unset, SubjectRolesOrganizationRole] = UNSET
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
        organization_role: Union[Unset, SubjectRolesOrganizationRole]
        if isinstance(_organization_role, Unset):
            organization_role = UNSET
        else:
            organization_role = SubjectRolesOrganizationRole(_organization_role)

        workspace_roles = []
        _workspace_roles = d.pop("workspaceRoles", UNSET)
        for workspace_roles_item_data in _workspace_roles or []:
            workspace_roles_item = WorkspaceRole.from_dict(workspace_roles_item_data)

            workspace_roles.append(workspace_roles_item)

        subject_roles = cls(
            deployment_roles=deployment_roles,
            organization_role=organization_role,
            workspace_roles=workspace_roles,
        )

        subject_roles.additional_properties = d
        return subject_roles

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
