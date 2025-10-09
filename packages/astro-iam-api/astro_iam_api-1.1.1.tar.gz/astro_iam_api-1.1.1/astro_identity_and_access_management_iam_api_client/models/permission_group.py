from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.permission_entry import PermissionEntry


T = TypeVar("T", bound="PermissionGroup")


@_attrs_define
class PermissionGroup:
    """
    Attributes:
        description (str): The permission group's description. Example: Astro notification channel defines where alert
            messages can be sent. For example, alert messages issued via email or slack..
        name (str): The permission group's name. Example: workspace.notificationChannels.
        permissions (list['PermissionEntry']): The permission group's permissions.
        scope (str): The permission group's scope. Example: Workspace NotificationChannels.
    """

    description: str
    name: str
    permissions: list["PermissionEntry"]
    scope: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        name = self.name

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.to_dict()
            permissions.append(permissions_item)

        scope = self.scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "name": name,
                "permissions": permissions,
                "scope": scope,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.permission_entry import PermissionEntry

        d = dict(src_dict)
        description = d.pop("description")

        name = d.pop("name")

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = PermissionEntry.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        scope = d.pop("scope")

        permission_group = cls(
            description=description,
            name=name,
            permissions=permissions,
            scope=scope,
        )

        permission_group.additional_properties = d
        return permission_group

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
