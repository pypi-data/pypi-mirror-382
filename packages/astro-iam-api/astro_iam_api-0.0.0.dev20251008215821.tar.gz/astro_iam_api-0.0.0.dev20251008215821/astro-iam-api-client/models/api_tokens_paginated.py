from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.api_token import ApiToken


T = TypeVar("T", bound="ApiTokensPaginated")


@_attrs_define
class ApiTokensPaginated:
    """
    Attributes:
        limit (int): The limit of values in this page. Example: 10.
        offset (int): The offset of values in this page.
        tokens (list['ApiToken']): The list of API tokens in this page.
        total_count (int): The total number of API tokens. Example: 100.
    """

    limit: int
    offset: int
    tokens: list["ApiToken"]
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        offset = self.offset

        tokens = []
        for tokens_item_data in self.tokens:
            tokens_item = tokens_item_data.to_dict()
            tokens.append(tokens_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "tokens": tokens,
                "totalCount": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_token import ApiToken

        d = dict(src_dict)
        limit = d.pop("limit")

        offset = d.pop("offset")

        tokens = []
        _tokens = d.pop("tokens")
        for tokens_item_data in _tokens:
            tokens_item = ApiToken.from_dict(tokens_item_data)

            tokens.append(tokens_item)

        total_count = d.pop("totalCount")

        api_tokens_paginated = cls(
            limit=limit,
            offset=offset,
            tokens=tokens,
            total_count=total_count,
        )

        api_tokens_paginated.additional_properties = d
        return api_tokens_paginated

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
