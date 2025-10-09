import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_subject_profile import BasicSubjectProfile


T = TypeVar("T", bound="AllowedIpAddressRange")


@_attrs_define
class AllowedIpAddressRange:
    """
    Attributes:
        created_at (datetime.datetime): The time when the allowed IP address range was created in UTC, formatted as
            `YYYY-MM-DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        id (str): The allowed IP address range's ID. Example: clm9sq6s0000008kz7uvl7yz7.
        ip_address_range (str): The allowed IP address range in CIDR format. Example: 1.1.1.1/32.
        organization_id (str): The  allowed IP address range's Organization ID. Example: clyt27999000008me3yp39wcp.
        updated_at (datetime.datetime): The time when the allowed IP address range was updated in UTC, formatted as
            `YYYY-MM-DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        created_by (Union[Unset, BasicSubjectProfile]):
        updated_by (Union[Unset, BasicSubjectProfile]):
    """

    created_at: datetime.datetime
    id: str
    ip_address_range: str
    organization_id: str
    updated_at: datetime.datetime
    created_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    updated_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = self.id

        ip_address_range = self.ip_address_range

        organization_id = self.organization_id

        updated_at = self.updated_at.isoformat()

        created_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.created_by, Unset):
            created_by = self.created_by.to_dict()

        updated_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.updated_by, Unset):
            updated_by = self.updated_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "id": id,
                "ipAddressRange": ip_address_range,
                "organizationId": organization_id,
                "updatedAt": updated_at,
            }
        )
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_subject_profile import BasicSubjectProfile

        d = dict(src_dict)
        created_at = isoparse(d.pop("createdAt"))

        id = d.pop("id")

        ip_address_range = d.pop("ipAddressRange")

        organization_id = d.pop("organizationId")

        updated_at = isoparse(d.pop("updatedAt"))

        _created_by = d.pop("createdBy", UNSET)
        created_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_created_by, Unset):
            created_by = UNSET
        else:
            created_by = BasicSubjectProfile.from_dict(_created_by)

        _updated_by = d.pop("updatedBy", UNSET)
        updated_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = BasicSubjectProfile.from_dict(_updated_by)

        allowed_ip_address_range = cls(
            created_at=created_at,
            id=id,
            ip_address_range=ip_address_range,
            organization_id=organization_id,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
        )

        allowed_ip_address_range.additional_properties = d
        return allowed_ip_address_range

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
