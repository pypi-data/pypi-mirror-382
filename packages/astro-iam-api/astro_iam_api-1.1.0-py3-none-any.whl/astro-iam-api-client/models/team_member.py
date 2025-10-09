import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TeamMember")


@_attrs_define
class TeamMember:
    """
    Attributes:
        user_id (str): The Team member's ID. Example: clma5vzk2000108k20jhq3f7n.
        username (str): The Team member's username. Example: user1@company.com.
        avatar_url (Union[Unset, str]): The URL for the Team member's profile image. Example: https://avatar.url.
        created_at (Union[Unset, datetime.datetime]): The time when the Team member was added in UTC, formatted as
            `YYYY-MM-DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        full_name (Union[Unset, str]): The Team member's full name. Example: Jane Doe.
    """

    user_id: str
    username: str
    avatar_url: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    full_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        username = self.username

        avatar_url = self.avatar_url

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        full_name = self.full_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userId": user_id,
                "username": username,
            }
        )
        if avatar_url is not UNSET:
            field_dict["avatarUrl"] = avatar_url
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if full_name is not UNSET:
            field_dict["fullName"] = full_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("userId")

        username = d.pop("username")

        avatar_url = d.pop("avatarUrl", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        full_name = d.pop("fullName", UNSET)

        team_member = cls(
            user_id=user_id,
            username=username,
            avatar_url=avatar_url,
            created_at=created_at,
            full_name=full_name,
        )

        team_member.additional_properties = d
        return team_member

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
