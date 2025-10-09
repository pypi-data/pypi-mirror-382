from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_user_invite_request_role import CreateUserInviteRequestRole

T = TypeVar("T", bound="CreateUserInviteRequest")


@_attrs_define
class CreateUserInviteRequest:
    """
    Attributes:
        invitee_email (str): The email of the user to invite. Example: user1@company.com.
        role (CreateUserInviteRequestRole): The user's Organization role. Example: ORGANIZATION_MEMBER.
    """

    invitee_email: str
    role: CreateUserInviteRequestRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        invitee_email = self.invitee_email

        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inviteeEmail": invitee_email,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        invitee_email = d.pop("inviteeEmail")

        role = CreateUserInviteRequestRole(d.pop("role"))

        create_user_invite_request = cls(
            invitee_email=invitee_email,
            role=role,
        )

        create_user_invite_request.additional_properties = d
        return create_user_invite_request

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
