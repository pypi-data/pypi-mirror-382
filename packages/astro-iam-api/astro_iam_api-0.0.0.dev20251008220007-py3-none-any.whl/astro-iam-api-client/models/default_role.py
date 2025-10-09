from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.default_role_scope_type import DefaultRoleScopeType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DefaultRole")


@_attrs_define
class DefaultRole:
    """
    Attributes:
        name (str): The role's name. Example: Deployment_Viewer.
        permissions (list[str]): The role's permissions. Example: ['deployment.get'].
        scope_type (DefaultRoleScopeType): The role's scope. Example: DEPLOYMENT.
        description (Union[Unset, str]): The role's description. Example: Subject can only view deployments..
    """

    name: str
    permissions: list[str]
    scope_type: DefaultRoleScopeType
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        permissions = self.permissions

        scope_type = self.scope_type.value

        description = self.description

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        permissions = cast(list[str], d.pop("permissions"))

        scope_type = DefaultRoleScopeType(d.pop("scopeType"))

        description = d.pop("description", UNSET)

        default_role = cls(
            name=name,
            permissions=permissions,
            scope_type=scope_type,
            description=description,
        )

        default_role.additional_properties = d
        return default_role

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
