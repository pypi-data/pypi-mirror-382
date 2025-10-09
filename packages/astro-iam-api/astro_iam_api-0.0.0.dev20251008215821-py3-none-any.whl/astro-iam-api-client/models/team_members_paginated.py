from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.team_member import TeamMember


T = TypeVar("T", bound="TeamMembersPaginated")


@_attrs_define
class TeamMembersPaginated:
    """
    Attributes:
        limit (int): The maximum number of Team members in one page. Example: 10.
        offset (int): The offset of the current page of Team members.
        team_members (list['TeamMember']): The list of Team members in the current page.
        total_count (int): The total number of Team members. Example: 100.
    """

    limit: int
    offset: int
    team_members: list["TeamMember"]
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        team_members = []
        for team_members_item_data in self.team_members:
            team_members_item = team_members_item_data.to_dict()
            team_members.append(team_members_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "teamMembers": team_members,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_member import TeamMember

        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        team_members = []
        _team_members = d.pop("teamMembers")
        for team_members_item_data in _team_members:
            team_members_item = TeamMember.from_dict(team_members_item_data)

            team_members.append(team_members_item)

        total_count = d.pop("totalCount")

        team_members_paginated = cls(
            limit=limit,
            offset=offset,
            team_members=team_members,
            total_count=total_count,
        )

        team_members_paginated.additional_properties = d
        return team_members_paginated

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
