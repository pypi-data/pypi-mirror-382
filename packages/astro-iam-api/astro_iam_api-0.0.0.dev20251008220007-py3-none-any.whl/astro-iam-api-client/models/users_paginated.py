from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="UsersPaginated")


@_attrs_define
class UsersPaginated:
    """
    Attributes:
        limit (int): The maximum number of users in one page. Example: 10.
        offset (int): The offset of the current page of users.
        total_count (int): The total number of users. Example: 100.
        users (list['User']): The list of users in the current page.
    """

    limit: int
    offset: int
    total_count: int
    users: list["User"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
                "users": users,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = User.from_dict(users_item_data)

            users.append(users_item)

        users_paginated = cls(
            limit=limit,
            offset=offset,
            total_count=total_count,
            users=users,
        )

        users_paginated.additional_properties = d
        return users_paginated

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
