from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cluster_options import ClusterOptions
from ...models.error import Error
from ...models.get_cluster_options_provider import GetClusterOptionsProvider
from ...models.get_cluster_options_type import GetClusterOptionsType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    provider: Union[Unset, GetClusterOptionsProvider] = UNSET,
    type_: GetClusterOptionsType,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_provider: Union[Unset, str] = UNSET
    if not isinstance(provider, Unset):
        json_provider = provider.value

    params["provider"] = json_provider

    json_type_ = type_.value
    params["type"] = json_type_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/cluster-options",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, list["ClusterOptions"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ClusterOptions.from_dict(response_200_item_data)

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
) -> Response[Union[Error, list["ClusterOptions"]]]:
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
    provider: Union[Unset, GetClusterOptionsProvider] = UNSET,
    type_: GetClusterOptionsType,
) -> Response[Union[Error, list["ClusterOptions"]]]:
    """Get cluster options

     Get all possible options for configuring a cluster.

    Args:
        organization_id (str):
        provider (Union[Unset, GetClusterOptionsProvider]):
        type_ (GetClusterOptionsType):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['ClusterOptions']]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        provider=provider,
        type_=type_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    provider: Union[Unset, GetClusterOptionsProvider] = UNSET,
    type_: GetClusterOptionsType,
) -> Optional[Union[Error, list["ClusterOptions"]]]:
    """Get cluster options

     Get all possible options for configuring a cluster.

    Args:
        organization_id (str):
        provider (Union[Unset, GetClusterOptionsProvider]):
        type_ (GetClusterOptionsType):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['ClusterOptions']]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        provider=provider,
        type_=type_,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    provider: Union[Unset, GetClusterOptionsProvider] = UNSET,
    type_: GetClusterOptionsType,
) -> Response[Union[Error, list["ClusterOptions"]]]:
    """Get cluster options

     Get all possible options for configuring a cluster.

    Args:
        organization_id (str):
        provider (Union[Unset, GetClusterOptionsProvider]):
        type_ (GetClusterOptionsType):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['ClusterOptions']]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        provider=provider,
        type_=type_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    provider: Union[Unset, GetClusterOptionsProvider] = UNSET,
    type_: GetClusterOptionsType,
) -> Optional[Union[Error, list["ClusterOptions"]]]:
    """Get cluster options

     Get all possible options for configuring a cluster.

    Args:
        organization_id (str):
        provider (Union[Unset, GetClusterOptionsProvider]):
        type_ (GetClusterOptionsType):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['ClusterOptions']]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            provider=provider,
            type_=type_,
        )
    ).parsed
