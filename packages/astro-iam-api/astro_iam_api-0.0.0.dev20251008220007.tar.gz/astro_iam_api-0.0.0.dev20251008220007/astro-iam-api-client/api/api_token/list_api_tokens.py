from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_tokens_paginated import ApiTokensPaginated
from ...models.error import Error
from ...models.list_api_tokens_sorts_item import ListApiTokensSortsItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    include_only_organization_tokens: Union[Unset, bool] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListApiTokensSortsItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["workspaceId"] = workspace_id

    params["deploymentId"] = deployment_id

    params["includeOnlyOrganizationTokens"] = include_only_organization_tokens

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
        "url": f"/organizations/{organization_id}/tokens",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ApiTokensPaginated, Error]]:
    if response.status_code == 200:
        response_200 = ApiTokensPaginated.from_dict(response.json())

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
) -> Response[Union[ApiTokensPaginated, Error]]:
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
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    include_only_organization_tokens: Union[Unset, bool] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListApiTokensSortsItem]] = UNSET,
) -> Response[Union[ApiTokensPaginated, Error]]:
    """List API tokens

     List information about all API tokens from an Organization. Filters on Workspace when Workspace ID
    is provided. When `includeOnlyOrganizationTokens` is `true`, only Organization API tokens are
    returned.

    Args:
        organization_id (str):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        include_only_organization_tokens (Union[Unset, bool]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListApiTokensSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiTokensPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        workspace_id=workspace_id,
        deployment_id=deployment_id,
        include_only_organization_tokens=include_only_organization_tokens,
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
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    include_only_organization_tokens: Union[Unset, bool] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListApiTokensSortsItem]] = UNSET,
) -> Optional[Union[ApiTokensPaginated, Error]]:
    """List API tokens

     List information about all API tokens from an Organization. Filters on Workspace when Workspace ID
    is provided. When `includeOnlyOrganizationTokens` is `true`, only Organization API tokens are
    returned.

    Args:
        organization_id (str):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        include_only_organization_tokens (Union[Unset, bool]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListApiTokensSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiTokensPaginated, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        workspace_id=workspace_id,
        deployment_id=deployment_id,
        include_only_organization_tokens=include_only_organization_tokens,
        offset=offset,
        limit=limit,
        sorts=sorts,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    include_only_organization_tokens: Union[Unset, bool] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListApiTokensSortsItem]] = UNSET,
) -> Response[Union[ApiTokensPaginated, Error]]:
    """List API tokens

     List information about all API tokens from an Organization. Filters on Workspace when Workspace ID
    is provided. When `includeOnlyOrganizationTokens` is `true`, only Organization API tokens are
    returned.

    Args:
        organization_id (str):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        include_only_organization_tokens (Union[Unset, bool]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListApiTokensSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiTokensPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        workspace_id=workspace_id,
        deployment_id=deployment_id,
        include_only_organization_tokens=include_only_organization_tokens,
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
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    include_only_organization_tokens: Union[Unset, bool] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListApiTokensSortsItem]] = UNSET,
) -> Optional[Union[ApiTokensPaginated, Error]]:
    """List API tokens

     List information about all API tokens from an Organization. Filters on Workspace when Workspace ID
    is provided. When `includeOnlyOrganizationTokens` is `true`, only Organization API tokens are
    returned.

    Args:
        organization_id (str):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        include_only_organization_tokens (Union[Unset, bool]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListApiTokensSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiTokensPaginated, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            workspace_id=workspace_id,
            deployment_id=deployment_id,
            include_only_organization_tokens=include_only_organization_tokens,
            offset=offset,
            limit=limit,
            sorts=sorts,
        )
    ).parsed
