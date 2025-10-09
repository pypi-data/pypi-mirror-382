from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.default_role import DefaultRole
    from ..models.role import Role


T = TypeVar("T", bound="RolesPaginated")


@_attrs_define
class RolesPaginated:
    """
    Attributes:
        limit (int): The number of custom roles returned. Example: 1.
        offset (int): The offset of the custom roles. Example: 1.
        roles (list['Role']): The list of custom roles.
        total_count (int): The total number of custom roles. Example: 1.
        default_roles (Union[Unset, list['DefaultRole']]): The list of default roles.
    """

    limit: int
    offset: int
    roles: list["Role"]
    total_count: int
    default_roles: Union[Unset, list["DefaultRole"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        roles = []
        for roles_item_data in self.roles:
            roles_item = roles_item_data.to_dict()
            roles.append(roles_item)

        total_count = self.total_count

        default_roles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.default_roles, Unset):
            default_roles = []
            for default_roles_item_data in self.default_roles:
                default_roles_item = default_roles_item_data.to_dict()
                default_roles.append(default_roles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "roles": roles,
                "totalCount": total_count,
            }
        )
        if default_roles is not UNSET:
            field_dict["defaultRoles"] = default_roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.default_role import DefaultRole
        from ..models.role import Role

        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        roles = []
        _roles = d.pop("roles")
        for roles_item_data in _roles:
            roles_item = Role.from_dict(roles_item_data)

            roles.append(roles_item)

        total_count = d.pop("totalCount")

        default_roles = []
        _default_roles = d.pop("defaultRoles", UNSET)
        for default_roles_item_data in _default_roles or []:
            default_roles_item = DefaultRole.from_dict(default_roles_item_data)

            default_roles.append(default_roles_item)

        roles_paginated = cls(
            limit=limit,
            offset=offset,
            roles=roles,
            total_count=total_count,
            default_roles=default_roles,
        )

        roles_paginated.additional_properties = d
        return roles_paginated

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
