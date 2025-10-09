from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_permission_groups_scope_type import ListPermissionGroupsScopeType
from ...models.permission_group import PermissionGroup
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    scope_type: Union[Unset, ListPermissionGroupsScopeType] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_scope_type: Union[Unset, str] = UNSET
    if not isinstance(scope_type, Unset):
        json_scope_type = scope_type.value

    params["scopeType"] = json_scope_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/authorization/permission-groups",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, list["PermissionGroup"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PermissionGroup.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, list["PermissionGroup"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    scope_type: Union[Unset, ListPermissionGroupsScopeType] = UNSET,
) -> Response[Union[Error, list["PermissionGroup"]]]:
    """List authorization permission groups

     List the available permissions you can grant to a custom role.

    Args:
        scope_type (Union[Unset, ListPermissionGroupsScopeType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['PermissionGroup']]]
    """

    kwargs = _get_kwargs(
        scope_type=scope_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    scope_type: Union[Unset, ListPermissionGroupsScopeType] = UNSET,
) -> Optional[Union[Error, list["PermissionGroup"]]]:
    """List authorization permission groups

     List the available permissions you can grant to a custom role.

    Args:
        scope_type (Union[Unset, ListPermissionGroupsScopeType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['PermissionGroup']]
    """

    return sync_detailed(
        client=client,
        scope_type=scope_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    scope_type: Union[Unset, ListPermissionGroupsScopeType] = UNSET,
) -> Response[Union[Error, list["PermissionGroup"]]]:
    """List authorization permission groups

     List the available permissions you can grant to a custom role.

    Args:
        scope_type (Union[Unset, ListPermissionGroupsScopeType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['PermissionGroup']]]
    """

    kwargs = _get_kwargs(
        scope_type=scope_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    scope_type: Union[Unset, ListPermissionGroupsScopeType] = UNSET,
) -> Optional[Union[Error, list["PermissionGroup"]]]:
    """List authorization permission groups

     List the available permissions you can grant to a custom role.

    Args:
        scope_type (Union[Unset, ListPermissionGroupsScopeType]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['PermissionGroup']]
    """

    return (
        await asyncio_detailed(
            client=client,
            scope_type=scope_type,
        )
    ).parsed
