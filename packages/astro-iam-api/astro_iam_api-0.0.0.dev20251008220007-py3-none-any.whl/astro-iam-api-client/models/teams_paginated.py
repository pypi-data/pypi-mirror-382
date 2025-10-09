from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.team import Team


T = TypeVar("T", bound="TeamsPaginated")


@_attrs_define
class TeamsPaginated:
    """
    Attributes:
        limit (int): The maximum number of Teams in one page. Example: 10.
        offset (int): The offset of the current page of Teams.
        teams (list['Team']): The list of Teams in the current page.
        total_count (int): The total number of Teams. Example: 100.
    """

    limit: int
    offset: int
    teams: list["Team"]
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        teams = []
        for teams_item_data in self.teams:
            teams_item = teams_item_data.to_dict()
            teams.append(teams_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "teams": teams,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team import Team

        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        teams = []
        _teams = d.pop("teams")
        for teams_item_data in _teams:
            teams_item = Team.from_dict(teams_item_data)

            teams.append(teams_item)

        total_count = d.pop("totalCount")

        teams_paginated = cls(
            limit=limit,
            offset=offset,
            teams=teams,
            total_count=total_count,
        )

        teams_paginated.additional_properties = d
        return teams_paginated

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
