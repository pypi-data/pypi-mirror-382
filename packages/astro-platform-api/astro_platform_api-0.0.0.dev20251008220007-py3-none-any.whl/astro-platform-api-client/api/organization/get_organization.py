from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.organization import Organization
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    is_look_up_only: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["isLookUpOnly"] = is_look_up_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, Organization]]:
    if response.status_code == 200:
        response_200 = Organization.from_dict(response.json())

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
) -> Response[Union[Error, Organization]]:
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
    is_look_up_only: Union[Unset, bool] = UNSET,
) -> Response[Union[Error, Organization]]:
    """Get an Organization

     Retrieve information about a specific Organization.

    Args:
        organization_id (str):
        is_look_up_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Organization]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        is_look_up_only=is_look_up_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    is_look_up_only: Union[Unset, bool] = UNSET,
) -> Optional[Union[Error, Organization]]:
    """Get an Organization

     Retrieve information about a specific Organization.

    Args:
        organization_id (str):
        is_look_up_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Organization]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        is_look_up_only=is_look_up_only,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    is_look_up_only: Union[Unset, bool] = UNSET,
) -> Response[Union[Error, Organization]]:
    """Get an Organization

     Retrieve information about a specific Organization.

    Args:
        organization_id (str):
        is_look_up_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Organization]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        is_look_up_only=is_look_up_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    is_look_up_only: Union[Unset, bool] = UNSET,
) -> Optional[Union[Error, Organization]]:
    """Get an Organization

     Retrieve information about a specific Organization.

    Args:
        organization_id (str):
        is_look_up_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Organization]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            is_look_up_only=is_look_up_only,
        )
    ).parsed
