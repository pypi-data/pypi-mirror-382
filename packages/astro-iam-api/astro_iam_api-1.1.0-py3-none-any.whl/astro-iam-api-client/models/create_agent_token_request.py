from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateAgentTokenRequest")


@_attrs_define
class CreateAgentTokenRequest:
    """
    Attributes:
        name (str): The name of the API token. Example: My token.
        description (Union[Unset, str]): The description for the API token. Example: This is my API token.
        token_expiry_period_in_days (Union[Unset, int]): The expiry period of the API token in days. If not specified,
            the token will never expire. Example: 30.
    """

    name: str
    description: Union[Unset, str] = UNSET
    token_expiry_period_in_days: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        token_expiry_period_in_days = self.token_expiry_period_in_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if token_expiry_period_in_days is not UNSET:
            field_dict["tokenExpiryPeriodInDays"] = token_expiry_period_in_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        token_expiry_period_in_days = d.pop("tokenExpiryPeriodInDays", UNSET)

        create_agent_token_request = cls(
            name=name,
            description=description,
            token_expiry_period_in_days=token_expiry_period_in_days,
        )

        create_agent_token_request.additional_properties = d
        return create_agent_token_request

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
