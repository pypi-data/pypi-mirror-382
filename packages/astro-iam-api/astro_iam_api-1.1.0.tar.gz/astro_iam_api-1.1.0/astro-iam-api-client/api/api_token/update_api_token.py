from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_token import ApiToken
from ...models.error import Error
from ...models.update_api_token_request import UpdateApiTokenRequest
from ...types import Response


def _get_kwargs(
    organization_id: str,
    token_id: str,
    *,
    body: UpdateApiTokenRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/organizations/{organization_id}/tokens/{token_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ApiToken, Error]]:
    if response.status_code == 200:
        response_200 = ApiToken.from_dict(response.json())

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
) -> Response[Union[ApiToken, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateApiTokenRequest,
) -> Response[Union[ApiToken, Error]]:
    """Update an API token

     Update the name and description of an API token.

    Args:
        organization_id (str):
        token_id (str):
        body (UpdateApiTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiToken, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        token_id=token_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateApiTokenRequest,
) -> Optional[Union[ApiToken, Error]]:
    """Update an API token

     Update the name and description of an API token.

    Args:
        organization_id (str):
        token_id (str):
        body (UpdateApiTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiToken, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        token_id=token_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateApiTokenRequest,
) -> Response[Union[ApiToken, Error]]:
    """Update an API token

     Update the name and description of an API token.

    Args:
        organization_id (str):
        token_id (str):
        body (UpdateApiTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiToken, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        token_id=token_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    token_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateApiTokenRequest,
) -> Optional[Union[ApiToken, Error]]:
    """Update an API token

     Update the name and description of an API token.

    Args:
        organization_id (str):
        token_id (str):
        body (UpdateApiTokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiToken, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            token_id=token_id,
            client=client,
            body=body,
        )
    ).parsed
