from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_api_token_request_type import CreateApiTokenRequestType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateApiTokenRequest")


@_attrs_define
class CreateApiTokenRequest:
    """
    Attributes:
        name (str): The name of the API token. Example: My token.
        role (str): The role of the API token. Example: WORKSPACE_OWNER.
        type_ (CreateApiTokenRequestType): The scope of the API token. Example: WORKSPACE.
        description (Union[Unset, str]): The description for the API token. Example: This is my API token.
        entity_id (Union[Unset, str]): The ID of the Workspace or Deployment to which the API token is scoped. It is
            required if `Type` is `WORKSPACE` or `DEPLOYMENT`. Example: clm8pxjjw000008l23jm08hyu.
        token_expiry_period_in_days (Union[Unset, int]): The expiry period of the API token in days. If not specified,
            the token will never expire. Example: 30.
    """

    name: str
    role: str
    type_: CreateApiTokenRequestType
    description: Union[Unset, str] = UNSET
    entity_id: Union[Unset, str] = UNSET
    token_expiry_period_in_days: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        role = self.role

        type_ = self.type_.value

        description = self.description

        entity_id = self.entity_id

        token_expiry_period_in_days = self.token_expiry_period_in_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "role": role,
                "type": type_,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if entity_id is not UNSET:
            field_dict["entityId"] = entity_id
        if token_expiry_period_in_days is not UNSET:
            field_dict["tokenExpiryPeriodInDays"] = token_expiry_period_in_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        role = d.pop("role")

        type_ = CreateApiTokenRequestType(d.pop("type"))

        description = d.pop("description", UNSET)

        entity_id = d.pop("entityId", UNSET)

        token_expiry_period_in_days = d.pop("tokenExpiryPeriodInDays", UNSET)

        create_api_token_request = cls(
            name=name,
            role=role,
            type_=type_,
            description=description,
            entity_id=entity_id,
            token_expiry_period_in_days=token_expiry_period_in_days,
        )

        create_api_token_request.additional_properties = d
        return create_api_token_request

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
