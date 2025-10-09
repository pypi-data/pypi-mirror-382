from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_team_request_organization_role import CreateTeamRequestOrganizationRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateTeamRequest")


@_attrs_define
class CreateTeamRequest:
    """
    Attributes:
        name (str): The Team's name. Example: My Team.
        description (Union[Unset, str]): The Team's description. Example: My Team description.
        member_ids (Union[Unset, list[str]]): The list of IDs for users to add to the Team. Example:
            ['clma67byh000008md1gr995ez'].
        organization_role (Union[Unset, CreateTeamRequestOrganizationRole]): The Team's Organization role. Example:
            ORGANIZATION_MEMBER.
    """

    name: str
    description: Union[Unset, str] = UNSET
    member_ids: Union[Unset, list[str]] = UNSET
    organization_role: Union[Unset, CreateTeamRequestOrganizationRole] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        member_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.member_ids, Unset):
            member_ids = self.member_ids

        organization_role: Union[Unset, str] = UNSET
        if not isinstance(self.organization_role, Unset):
            organization_role = self.organization_role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if member_ids is not UNSET:
            field_dict["memberIds"] = member_ids
        if organization_role is not UNSET:
            field_dict["organizationRole"] = organization_role

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        member_ids = cast(list[str], d.pop("memberIds", UNSET))

        _organization_role = d.pop("organizationRole", UNSET)
        organization_role: Union[Unset, CreateTeamRequestOrganizationRole]
        if isinstance(_organization_role, Unset):
            organization_role = UNSET
        else:
            organization_role = CreateTeamRequestOrganizationRole(_organization_role)

        create_team_request = cls(
            name=name,
            description=description,
            member_ids=member_ids,
            organization_role=organization_role,
        )

        create_team_request.additional_properties = d
        return create_team_request

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
