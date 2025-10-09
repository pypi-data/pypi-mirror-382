from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cluster import Cluster
from ...models.error import Error
from ...models.update_dedicated_cluster_request import UpdateDedicatedClusterRequest
from ...models.update_hybrid_cluster_request import UpdateHybridClusterRequest
from ...types import Response


def _get_kwargs(
    organization_id: str,
    cluster_id: str,
    *,
    body: Union["UpdateDedicatedClusterRequest", "UpdateHybridClusterRequest"],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/organizations/{organization_id}/clusters/{cluster_id}",
    }

    _kwargs["json"]: dict[str, Any]
    if isinstance(body, UpdateDedicatedClusterRequest):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Cluster, Error]]:
    if response.status_code == 200:
        response_200 = Cluster.from_dict(response.json())

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

    if response.status_code == 412:
        response_412 = Error.from_dict(response.json())

        return response_412

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Cluster, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    cluster_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["UpdateDedicatedClusterRequest", "UpdateHybridClusterRequest"],
) -> Response[Union[Cluster, Error]]:
    """Update a cluster

     Update a cluster in the Organization.

    Args:
        organization_id (str):
        cluster_id (str):
        body (Union['UpdateDedicatedClusterRequest', 'UpdateHybridClusterRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Cluster, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        cluster_id=cluster_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    cluster_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["UpdateDedicatedClusterRequest", "UpdateHybridClusterRequest"],
) -> Optional[Union[Cluster, Error]]:
    """Update a cluster

     Update a cluster in the Organization.

    Args:
        organization_id (str):
        cluster_id (str):
        body (Union['UpdateDedicatedClusterRequest', 'UpdateHybridClusterRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Cluster, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        cluster_id=cluster_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    cluster_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["UpdateDedicatedClusterRequest", "UpdateHybridClusterRequest"],
) -> Response[Union[Cluster, Error]]:
    """Update a cluster

     Update a cluster in the Organization.

    Args:
        organization_id (str):
        cluster_id (str):
        body (Union['UpdateDedicatedClusterRequest', 'UpdateHybridClusterRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Cluster, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        cluster_id=cluster_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    cluster_id: str,
    *,
    client: AuthenticatedClient,
    body: Union["UpdateDedicatedClusterRequest", "UpdateHybridClusterRequest"],
) -> Optional[Union[Cluster, Error]]:
    """Update a cluster

     Update a cluster in the Organization.

    Args:
        organization_id (str):
        cluster_id (str):
        body (Union['UpdateDedicatedClusterRequest', 'UpdateHybridClusterRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Cluster, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            cluster_id=cluster_id,
            client=client,
            body=body,
        )
    ).parsed
