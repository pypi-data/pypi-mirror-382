from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.allowed_ip_address_range import AllowedIpAddressRange


T = TypeVar("T", bound="AllowedIpAddressRangesPaginated")


@_attrs_define
class AllowedIpAddressRangesPaginated:
    """
    Attributes:
        allowed_ip_address_ranges (list['AllowedIpAddressRange']):
        limit (int): The maximum number of allowed IP address ranges in one page. Example: 10.
        offset (int): The offset of the current page of allowed IP address ranges.
        total_count (int): The total number of allowed IP address ranges. Example: 10.
    """

    allowed_ip_address_ranges: list["AllowedIpAddressRange"]
    limit: int
    offset: int
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed_ip_address_ranges = []
        for allowed_ip_address_ranges_item_data in self.allowed_ip_address_ranges:
            allowed_ip_address_ranges_item = allowed_ip_address_ranges_item_data.to_dict()
            allowed_ip_address_ranges.append(allowed_ip_address_ranges_item)

        limit = self.limit

        offset = self.offset

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allowedIpAddressRanges": allowed_ip_address_ranges,
                "limit": limit,
                "offset": offset,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.allowed_ip_address_range import AllowedIpAddressRange

        d = dict(src_dict)
        allowed_ip_address_ranges = []
        _allowed_ip_address_ranges = d.pop("allowedIpAddressRanges")
        for allowed_ip_address_ranges_item_data in _allowed_ip_address_ranges:
            allowed_ip_address_ranges_item = AllowedIpAddressRange.from_dict(allowed_ip_address_ranges_item_data)

            allowed_ip_address_ranges.append(allowed_ip_address_ranges_item)

        limit = d.pop("limit")

        offset = d.pop("offset")

        total_count = d.pop("totalCount")

        allowed_ip_address_ranges_paginated = cls(
            allowed_ip_address_ranges=allowed_ip_address_ranges,
            limit=limit,
            offset=offset,
            total_count=total_count,
        )

        allowed_ip_address_ranges_paginated.additional_properties = d
        return allowed_ip_address_ranges_paginated

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
