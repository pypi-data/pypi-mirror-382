from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile


T = TypeVar("T", bound="Invite")


@_attrs_define
class Invite:
    """
    Attributes:
        expires_at (str): The time when the invite is expired in UTC, formatted as `YYYY-MM-DDTHH:MM:SSZ`. Example:
            2022-11-22T04:37:12Z.
        invite_id (str): The invite ID. Example: clm9t1g17000008jmfsw20lsz.
        invitee (BasicSubjectProfile):
        inviter (BasicSubjectProfile):
        organization_id (str): The ID of the Organization where the invite was sent. Example: clm9t0gbt000108jv4f1cfu8u.
        organization_name (Union[Unset, str]): The name of the Organization where the invite was sent. Example: My
            Organization.
        user_id (Union[Unset, str]): The ID for the user who was invited. Example: clm9t060z000008jv3mira7x5.
    """

    expires_at: str
    invite_id: str
    invitee: "BasicSubjectProfile"
    inviter: "BasicSubjectProfile"
    organization_id: str
    organization_name: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expires_at = self.expires_at

        invite_id = self.invite_id

        invitee = self.invitee.to_dict()

        inviter = self.inviter.to_dict()

        organization_id = self.organization_id

        organization_name = self.organization_name

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "expiresAt": expires_at,
                "inviteId": invite_id,
                "invitee": invitee,
                "inviter": inviter,
                "organizationId": organization_id,
            }
        )
        if organization_name is not UNSET:
            field_dict["organizationName"] = organization_name
        if user_id is not UNSET:
            field_dict["userId"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile

        d = dict(src_dict)
        expires_at = d.pop("expiresAt")

        invite_id = d.pop("inviteId")

        invitee = BasicSubjectProfile.from_dict(d.pop("invitee"))

        inviter = BasicSubjectProfile.from_dict(d.pop("inviter"))

        organization_id = d.pop("organizationId")

        organization_name = d.pop("organizationName", UNSET)

        user_id = d.pop("userId", UNSET)

        invite = cls(
            expires_at=expires_at,
            invite_id=invite_id,
            invitee=invitee,
            inviter=inviter,
            organization_id=organization_id,
            organization_name=organization_name,
            user_id=user_id,
        )

        invite.additional_properties = d
        return invite

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
