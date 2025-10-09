from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.clusters_paginated import ClustersPaginated
from ...models.error import Error
from ...models.list_clusters_provider import ListClustersProvider
from ...models.list_clusters_sorts_item import ListClustersSortsItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    names: Union[Unset, list[str]] = UNSET,
    provider: Union[Unset, ListClustersProvider] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListClustersSortsItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_names: Union[Unset, list[str]] = UNSET
    if not isinstance(names, Unset):
        json_names = names

    params["names"] = json_names

    json_provider: Union[Unset, str] = UNSET
    if not isinstance(provider, Unset):
        json_provider = provider.value

    params["provider"] = json_provider

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
        "url": f"/organizations/{organization_id}/clusters",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ClustersPaginated, Error]]:
    if response.status_code == 200:
        response_200 = ClustersPaginated.from_dict(response.json())

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
) -> Response[Union[ClustersPaginated, Error]]:
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
    names: Union[Unset, list[str]] = UNSET,
    provider: Union[Unset, ListClustersProvider] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListClustersSortsItem]] = UNSET,
) -> Response[Union[ClustersPaginated, Error]]:
    """List clusters

     List clusters in an Organization.

    Args:
        organization_id (str):
        names (Union[Unset, list[str]]):
        provider (Union[Unset, ListClustersProvider]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListClustersSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClustersPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        names=names,
        provider=provider,
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
    names: Union[Unset, list[str]] = UNSET,
    provider: Union[Unset, ListClustersProvider] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListClustersSortsItem]] = UNSET,
) -> Optional[Union[ClustersPaginated, Error]]:
    """List clusters

     List clusters in an Organization.

    Args:
        organization_id (str):
        names (Union[Unset, list[str]]):
        provider (Union[Unset, ListClustersProvider]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListClustersSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClustersPaginated, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        names=names,
        provider=provider,
        offset=offset,
        limit=limit,
        sorts=sorts,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    names: Union[Unset, list[str]] = UNSET,
    provider: Union[Unset, ListClustersProvider] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListClustersSortsItem]] = UNSET,
) -> Response[Union[ClustersPaginated, Error]]:
    """List clusters

     List clusters in an Organization.

    Args:
        organization_id (str):
        names (Union[Unset, list[str]]):
        provider (Union[Unset, ListClustersProvider]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListClustersSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ClustersPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        names=names,
        provider=provider,
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
    names: Union[Unset, list[str]] = UNSET,
    provider: Union[Unset, ListClustersProvider] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListClustersSortsItem]] = UNSET,
) -> Optional[Union[ClustersPaginated, Error]]:
    """List clusters

     List clusters in an Organization.

    Args:
        organization_id (str):
        names (Union[Unset, list[str]]):
        provider (Union[Unset, ListClustersProvider]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListClustersSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ClustersPaginated, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            names=names,
            provider=provider,
            offset=offset,
            limit=limit,
            sorts=sorts,
        )
    ).parsed
