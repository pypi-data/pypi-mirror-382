from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.role_scope_type import RoleScopeType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile


T = TypeVar("T", bound="Role")


@_attrs_define
class Role:
    """
    Attributes:
        created_at (str): The time the role was created.
        created_by (BasicSubjectProfile):
        id (str): The role's ID. Example: cluc9tapx000901qn2xrgqdmn.
        name (str): The role's name. Example: Deployment_Viewer.
        restricted_workspace_ids (list[str]): The IDs of Workspaces that the role is restricted to. Example:
            ['cldbvzoi20182g8odxt8ehi5i'].
        scope_type (RoleScopeType): The role's scope. Example: DEPLOYMENT.
        updated_at (str): The time the role was last updated.
        updated_by (BasicSubjectProfile):
        description (Union[Unset, str]): The role's description. Example: Subject can only view deployments..
    """

    created_at: str
    created_by: "BasicSubjectProfile"
    id: str
    name: str
    restricted_workspace_ids: list[str]
    scope_type: RoleScopeType
    updated_at: str
    updated_by: "BasicSubjectProfile"
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at

        created_by = self.created_by.to_dict()

        id = self.id

        name = self.name

        restricted_workspace_ids = self.restricted_workspace_ids

        scope_type = self.scope_type.value

        updated_at = self.updated_at

        updated_by = self.updated_by.to_dict()

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "createdBy": created_by,
                "id": id,
                "name": name,
                "restrictedWorkspaceIds": restricted_workspace_ids,
                "scopeType": scope_type,
                "updatedAt": updated_at,
                "updatedBy": updated_by,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile

        d = dict(src_dict)
        created_at = d.pop("createdAt")

        created_by = BasicSubjectProfile.from_dict(d.pop("createdBy"))

        id = d.pop("id")

        name = d.pop("name")

        restricted_workspace_ids = cast(list[str], d.pop("restrictedWorkspaceIds"))

        scope_type = RoleScopeType(d.pop("scopeType"))

        updated_at = d.pop("updatedAt")

        updated_by = BasicSubjectProfile.from_dict(d.pop("updatedBy"))

        description = d.pop("description", UNSET)

        role = cls(
            created_at=created_at,
            created_by=created_by,
            id=id,
            name=name,
            restricted_workspace_ids=restricted_workspace_ids,
            scope_type=scope_type,
            updated_at=updated_at,
            updated_by=updated_by,
            description=description,
        )

        role.additional_properties = d
        return role

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
