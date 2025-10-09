from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_role_templates_scope_types_item import ListRoleTemplatesScopeTypesItem
from ...models.role_template import RoleTemplate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    scope_types: Union[Unset, list[ListRoleTemplatesScopeTypesItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_scope_types: Union[Unset, list[str]] = UNSET
    if not isinstance(scope_types, Unset):
        json_scope_types = []
        for scope_types_item_data in scope_types:
            scope_types_item = scope_types_item_data.value
            json_scope_types.append(scope_types_item)

    params["scopeTypes"] = json_scope_types

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/role-templates",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, list["RoleTemplate"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = RoleTemplate.from_dict(response_200_item_data)

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
) -> Response[Union[Error, list["RoleTemplate"]]]:
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
    scope_types: Union[Unset, list[ListRoleTemplatesScopeTypesItem]] = UNSET,
) -> Response[Union[Error, list["RoleTemplate"]]]:
    """Get role templates

     Get a list of available role templates in an Organization. A role template can be used as the basis
    for creating a new custom role.

    Args:
        organization_id (str):
        scope_types (Union[Unset, list[ListRoleTemplatesScopeTypesItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['RoleTemplate']]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        scope_types=scope_types,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    scope_types: Union[Unset, list[ListRoleTemplatesScopeTypesItem]] = UNSET,
) -> Optional[Union[Error, list["RoleTemplate"]]]:
    """Get role templates

     Get a list of available role templates in an Organization. A role template can be used as the basis
    for creating a new custom role.

    Args:
        organization_id (str):
        scope_types (Union[Unset, list[ListRoleTemplatesScopeTypesItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['RoleTemplate']]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        scope_types=scope_types,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    scope_types: Union[Unset, list[ListRoleTemplatesScopeTypesItem]] = UNSET,
) -> Response[Union[Error, list["RoleTemplate"]]]:
    """Get role templates

     Get a list of available role templates in an Organization. A role template can be used as the basis
    for creating a new custom role.

    Args:
        organization_id (str):
        scope_types (Union[Unset, list[ListRoleTemplatesScopeTypesItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['RoleTemplate']]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        scope_types=scope_types,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    scope_types: Union[Unset, list[ListRoleTemplatesScopeTypesItem]] = UNSET,
) -> Optional[Union[Error, list["RoleTemplate"]]]:
    """Get role templates

     Get a list of available role templates in an Organization. A role template can be used as the basis
    for creating a new custom role.

    Args:
        organization_id (str):
        scope_types (Union[Unset, list[ListRoleTemplatesScopeTypesItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['RoleTemplate']]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            scope_types=scope_types,
        )
    ).parsed
