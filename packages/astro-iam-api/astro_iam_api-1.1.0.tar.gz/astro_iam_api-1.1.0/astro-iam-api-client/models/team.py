import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.team_organization_role import TeamOrganizationRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile
    from ..models.deployment_role import DeploymentRole
    from ..models.workspace_role import WorkspaceRole


T = TypeVar("T", bound="Team")


@_attrs_define
class Team:
    """
    Attributes:
        created_at (datetime.datetime): The time when the Team was created in UTC, formatted as `YYYY-MM-DDTHH:MM:SSZ`.
            Example: 2022-11-22T04:37:12Z.
        id (str): The Team's ID. Example: clma5ftgk000008mhgev00k7d.
        is_idp_managed (bool): Whether the Team is managed by an identity provider (IdP).
        name (str): The Team's name. Example: My Team.
        organization_id (str): The ID of the Organization to which the Team belongs. Example: clma5g8q6000108mh88g27k1y.
        organization_role (TeamOrganizationRole): The Team's Organization role. Example: ORGANIZATION_MEMBER.
        updated_at (datetime.datetime): The time when the Team was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        created_by (Union[Unset, BasicSubjectProfile]):
        deployment_roles (Union[Unset, list['DeploymentRole']]): The Team's role in each Deployment it belongs to.
        description (Union[Unset, str]): The Team's description. Example: My Team description.
        roles_count (Union[Unset, int]): The number of roles the Team has. Example: 1.
        updated_by (Union[Unset, BasicSubjectProfile]):
        workspace_roles (Union[Unset, list['WorkspaceRole']]): The Team's role in each Workspace it belongs to.
    """

    created_at: datetime.datetime
    id: str
    is_idp_managed: bool
    name: str
    organization_id: str
    organization_role: TeamOrganizationRole
    updated_at: datetime.datetime
    created_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    deployment_roles: Union[Unset, list["DeploymentRole"]] = UNSET
    description: Union[Unset, str] = UNSET
    roles_count: Union[Unset, int] = UNSET
    updated_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    workspace_roles: Union[Unset, list["WorkspaceRole"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = self.id

        is_idp_managed = self.is_idp_managed

        name = self.name

        organization_id = self.organization_id

        organization_role = self.organization_role.value

        updated_at = self.updated_at.isoformat()

        created_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.created_by, Unset):
            created_by = self.created_by.to_dict()

        deployment_roles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.deployment_roles, Unset):
            deployment_roles = []
            for deployment_roles_item_data in self.deployment_roles:
                deployment_roles_item = deployment_roles_item_data.to_dict()
                deployment_roles.append(deployment_roles_item)

        description = self.description

        roles_count = self.roles_count

        updated_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.updated_by, Unset):
            updated_by = self.updated_by.to_dict()

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
                "createdAt": created_at,
                "id": id,
                "isIdpManaged": is_idp_managed,
                "name": name,
                "organizationId": organization_id,
                "organizationRole": organization_role,
                "updatedAt": updated_at,
            }
        )
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if deployment_roles is not UNSET:
            field_dict["deploymentRoles"] = deployment_roles
        if description is not UNSET:
            field_dict["description"] = description
        if roles_count is not UNSET:
            field_dict["rolesCount"] = roles_count
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by
        if workspace_roles is not UNSET:
            field_dict["workspaceRoles"] = workspace_roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile
        from ..models.deployment_role import DeploymentRole
        from ..models.workspace_role import WorkspaceRole

        d = dict(src_dict)
        created_at = isoparse(d.pop("createdAt"))

        id = d.pop("id")

        is_idp_managed = d.pop("isIdpManaged")

        name = d.pop("name")

        organization_id = d.pop("organizationId")

        organization_role = TeamOrganizationRole(d.pop("organizationRole"))

        updated_at = isoparse(d.pop("updatedAt"))

        _created_by = d.pop("createdBy", UNSET)
        created_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_created_by, Unset):
            created_by = UNSET
        else:
            created_by = BasicSubjectProfile.from_dict(_created_by)

        deployment_roles = []
        _deployment_roles = d.pop("deploymentRoles", UNSET)
        for deployment_roles_item_data in _deployment_roles or []:
            deployment_roles_item = DeploymentRole.from_dict(deployment_roles_item_data)

            deployment_roles.append(deployment_roles_item)

        description = d.pop("description", UNSET)

        roles_count = d.pop("rolesCount", UNSET)

        _updated_by = d.pop("updatedBy", UNSET)
        updated_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = BasicSubjectProfile.from_dict(_updated_by)

        workspace_roles = []
        _workspace_roles = d.pop("workspaceRoles", UNSET)
        for workspace_roles_item_data in _workspace_roles or []:
            workspace_roles_item = WorkspaceRole.from_dict(workspace_roles_item_data)

            workspace_roles.append(workspace_roles_item)

        team = cls(
            created_at=created_at,
            id=id,
            is_idp_managed=is_idp_managed,
            name=name,
            organization_id=organization_id,
            organization_role=organization_role,
            updated_at=updated_at,
            created_by=created_by,
            deployment_roles=deployment_roles,
            description=description,
            roles_count=roles_count,
            updated_by=updated_by,
            workspace_roles=workspace_roles,
        )

        team.additional_properties = d
        return team

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
