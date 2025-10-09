from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.api_token_role_entity_type import ApiTokenRoleEntityType

T = TypeVar("T", bound="ApiTokenRole")


@_attrs_define
class ApiTokenRole:
    """
    Attributes:
        entity_id (str): The ID of the entity to which the API token is scoped for. For example, for Workspace API
            tokens, this is the Workspace ID. Example: clm8sgvai000008l794psbkdv.
        entity_type (ApiTokenRoleEntityType): The type of the entity to which the API token is scoped for. Example:
            WORKSPACE.
        role (str): The role of the API token. Example: WORKSPACE_MEMBER.
    """

    entity_id: str
    entity_type: ApiTokenRoleEntityType
    role: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_id = self.entity_id

        entity_type = self.entity_type.value

        role = self.role

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entityId": entity_id,
                "entityType": entity_type,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entity_id = d.pop("entityId")

        entity_type = ApiTokenRoleEntityType(d.pop("entityType"))

        role = d.pop("role")

        api_token_role = cls(
            entity_id=entity_id,
            entity_type=entity_type,
            role=role,
        )

        api_token_role.additional_properties = d
        return api_token_role

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
