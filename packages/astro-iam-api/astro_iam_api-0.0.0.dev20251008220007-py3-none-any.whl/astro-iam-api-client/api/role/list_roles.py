from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_roles_scope_types_item import ListRolesScopeTypesItem
from ...models.list_roles_sorts_item import ListRolesSortsItem
from ...models.roles_paginated import RolesPaginated
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    include_default_roles: Union[Unset, bool] = UNSET,
    scope_types: Union[Unset, list[ListRolesScopeTypesItem]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListRolesSortsItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["includeDefaultRoles"] = include_default_roles

    json_scope_types: Union[Unset, list[str]] = UNSET
    if not isinstance(scope_types, Unset):
        json_scope_types = []
        for scope_types_item_data in scope_types:
            scope_types_item = scope_types_item_data.value
            json_scope_types.append(scope_types_item)

    params["scopeTypes"] = json_scope_types

    params["offset"] = offset

    params["limit"] = limit

    json_sorts: Union[Unset, list[str]] = UNSET
    if not isinstance(sorts, Unset):
        json_sorts = []
        for sorts_item_data in sorts:
            sorts_item = sorts_item_data.value
            json_sorts.append(sorts_item)

    params["sorts"] = json_sorts

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/roles",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, RolesPaginated]]:
    if response.status_code == 200:
        response_200 = RolesPaginated.from_dict(response.json())

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

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, RolesPaginated]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    include_default_roles: Union[Unset, bool] = UNSET,
    scope_types: Union[Unset, list[ListRolesScopeTypesItem]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListRolesSortsItem]] = UNSET,
) -> Response[Union[Error, RolesPaginated]]:
    """List roles

     List available user roles in an Organization.

    Args:
        organization_id (str):
        include_default_roles (Union[Unset, bool]):
        scope_types (Union[Unset, list[ListRolesScopeTypesItem]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListRolesSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, RolesPaginated]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        include_default_roles=include_default_roles,
        scope_types=scope_types,
        offset=offset,
        limit=limit,
        sorts=sorts,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    include_default_roles: Union[Unset, bool] = UNSET,
    scope_types: Union[Unset, list[ListRolesScopeTypesItem]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListRolesSortsItem]] = UNSET,
) -> Optional[Union[Error, RolesPaginated]]:
    """List roles

     List available user roles in an Organization.

    Args:
        organization_id (str):
        include_default_roles (Union[Unset, bool]):
        scope_types (Union[Unset, list[ListRolesScopeTypesItem]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListRolesSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, RolesPaginated]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        include_default_roles=include_default_roles,
        scope_types=scope_types,
        offset=offset,
        limit=limit,
        sorts=sorts,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    include_default_roles: Union[Unset, bool] = UNSET,
    scope_types: Union[Unset, list[ListRolesScopeTypesItem]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListRolesSortsItem]] = UNSET,
) -> Response[Union[Error, RolesPaginated]]:
    """List roles

     List available user roles in an Organization.

    Args:
        organization_id (str):
        include_default_roles (Union[Unset, bool]):
        scope_types (Union[Unset, list[ListRolesScopeTypesItem]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListRolesSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, RolesPaginated]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        include_default_roles=include_default_roles,
        scope_types=scope_types,
        offset=offset,
        limit=limit,
        sorts=sorts,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    include_default_roles: Union[Unset, bool] = UNSET,
    scope_types: Union[Unset, list[ListRolesScopeTypesItem]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListRolesSortsItem]] = UNSET,
) -> Optional[Union[Error, RolesPaginated]]:
    """List roles

     List available user roles in an Organization.

    Args:
        organization_id (str):
        include_default_roles (Union[Unset, bool]):
        scope_types (Union[Unset, list[ListRolesScopeTypesItem]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListRolesSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, RolesPaginated]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            include_default_roles=include_default_roles,
            scope_types=scope_types,
            offset=offset,
            limit=limit,
            sorts=sorts,
        )
    ).parsed
