import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.api_token_type import ApiTokenType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_token_role import ApiTokenRole
    from ..models.basic_subject_profile import BasicSubjectProfile


T = TypeVar("T", bound="ApiToken")


@_attrs_define
class ApiToken:
    """
    Attributes:
        created_at (datetime.datetime): The time when the API token was created in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        description (str): The description of the API token. Example: my token description.
        id (str): The API token's ID. Example: clm8q7f6q000008lcgyougpsk.
        name (str): The name of the API token. Example: My token.
        short_token (str): The short value of the API token. Example: short-token.
        start_at (datetime.datetime): The time when the API token will become valid in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        type_ (ApiTokenType): The type of the API token. Example: WORKSPACE.
        updated_at (datetime.datetime): The time when the API token was last updated in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        created_by (Union[Unset, BasicSubjectProfile]):
        end_at (Union[Unset, datetime.datetime]): The time when the API token expires in UTC, formatted as `YYYY-MM-
            DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        expiry_period_in_days (Union[Unset, int]): The expiry period of the API token in days. Example: 30.
        last_used_at (Union[Unset, datetime.datetime]): The time when the API token was last used in UTC, formatted as
            `YYYY-MM-DDTHH:MM:SSZ`. Example: 2022-11-22T04:37:12Z.
        roles (Union[Unset, list['ApiTokenRole']]): The roles of the API token.
        token (Union[Unset, str]): The value of the API token. Example: token.
        updated_by (Union[Unset, BasicSubjectProfile]):
    """

    created_at: datetime.datetime
    description: str
    id: str
    name: str
    short_token: str
    start_at: datetime.datetime
    type_: ApiTokenType
    updated_at: datetime.datetime
    created_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    end_at: Union[Unset, datetime.datetime] = UNSET
    expiry_period_in_days: Union[Unset, int] = UNSET
    last_used_at: Union[Unset, datetime.datetime] = UNSET
    roles: Union[Unset, list["ApiTokenRole"]] = UNSET
    token: Union[Unset, str] = UNSET
    updated_by: Union[Unset, "BasicSubjectProfile"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        description = self.description

        id = self.id

        name = self.name

        short_token = self.short_token

        start_at = self.start_at.isoformat()

        type_ = self.type_.value

        updated_at = self.updated_at.isoformat()

        created_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.created_by, Unset):
            created_by = self.created_by.to_dict()

        end_at: Union[Unset, str] = UNSET
        if not isinstance(self.end_at, Unset):
            end_at = self.end_at.isoformat()

        expiry_period_in_days = self.expiry_period_in_days

        last_used_at: Union[Unset, str] = UNSET
        if not isinstance(self.last_used_at, Unset):
            last_used_at = self.last_used_at.isoformat()

        roles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = []
            for roles_item_data in self.roles:
                roles_item = roles_item_data.to_dict()
                roles.append(roles_item)

        token = self.token

        updated_by: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.updated_by, Unset):
            updated_by = self.updated_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "description": description,
                "id": id,
                "name": name,
                "shortToken": short_token,
                "startAt": start_at,
                "type": type_,
                "updatedAt": updated_at,
            }
        )
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if end_at is not UNSET:
            field_dict["endAt"] = end_at
        if expiry_period_in_days is not UNSET:
            field_dict["expiryPeriodInDays"] = expiry_period_in_days
        if last_used_at is not UNSET:
            field_dict["lastUsedAt"] = last_used_at
        if roles is not UNSET:
            field_dict["roles"] = roles
        if token is not UNSET:
            field_dict["token"] = token
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_token_role import ApiTokenRole
        from ..models.basic_subject_profile import BasicSubjectProfile

        d = dict(src_dict)
        created_at = isoparse(d.pop("createdAt"))

        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        short_token = d.pop("shortToken")

        start_at = isoparse(d.pop("startAt"))

        type_ = ApiTokenType(d.pop("type"))

        updated_at = isoparse(d.pop("updatedAt"))

        _created_by = d.pop("createdBy", UNSET)
        created_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_created_by, Unset):
            created_by = UNSET
        else:
            created_by = BasicSubjectProfile.from_dict(_created_by)

        _end_at = d.pop("endAt", UNSET)
        end_at: Union[Unset, datetime.datetime]
        if isinstance(_end_at, Unset):
            end_at = UNSET
        else:
            end_at = isoparse(_end_at)

        expiry_period_in_days = d.pop("expiryPeriodInDays", UNSET)

        _last_used_at = d.pop("lastUsedAt", UNSET)
        last_used_at: Union[Unset, datetime.datetime]
        if isinstance(_last_used_at, Unset):
            last_used_at = UNSET
        else:
            last_used_at = isoparse(_last_used_at)

        roles = []
        _roles = d.pop("roles", UNSET)
        for roles_item_data in _roles or []:
            roles_item = ApiTokenRole.from_dict(roles_item_data)

            roles.append(roles_item)

        token = d.pop("token", UNSET)

        _updated_by = d.pop("updatedBy", UNSET)
        updated_by: Union[Unset, BasicSubjectProfile]
        if isinstance(_updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = BasicSubjectProfile.from_dict(_updated_by)

        api_token = cls(
            created_at=created_at,
            description=description,
            id=id,
            name=name,
            short_token=short_token,
            start_at=start_at,
            type_=type_,
            updated_at=updated_at,
            created_by=created_by,
            end_at=end_at,
            expiry_period_in_days=expiry_period_in_days,
            last_used_at=last_used_at,
            roles=roles,
            token=token,
            updated_by=updated_by,
        )

        api_token.additional_properties = d
        return api_token

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
