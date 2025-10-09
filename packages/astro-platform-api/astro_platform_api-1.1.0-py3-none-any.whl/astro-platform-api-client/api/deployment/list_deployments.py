from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployments_paginated import DeploymentsPaginated
from ...models.error import Error
from ...models.list_deployments_sorts_item import ListDeploymentsSortsItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    names: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListDeploymentsSortsItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_deployment_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(deployment_ids, Unset):
        json_deployment_ids = deployment_ids

    params["deploymentIds"] = json_deployment_ids

    json_names: Union[Unset, list[str]] = UNSET
    if not isinstance(names, Unset):
        json_names = names

    params["names"] = json_names

    json_workspace_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(workspace_ids, Unset):
        json_workspace_ids = workspace_ids

    params["workspaceIds"] = json_workspace_ids

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
        "url": f"/organizations/{organization_id}/deployments",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DeploymentsPaginated, Error]]:
    if response.status_code == 200:
        response_200 = DeploymentsPaginated.from_dict(response.json())

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
) -> Response[Union[DeploymentsPaginated, Error]]:
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
    deployment_ids: Union[Unset, list[str]] = UNSET,
    names: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListDeploymentsSortsItem]] = UNSET,
) -> Response[Union[DeploymentsPaginated, Error]]:
    """List Deployments

     List Deployments in an Organization.

    Args:
        organization_id (str):
        deployment_ids (Union[Unset, list[str]]):
        names (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListDeploymentsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeploymentsPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        deployment_ids=deployment_ids,
        names=names,
        workspace_ids=workspace_ids,
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
    deployment_ids: Union[Unset, list[str]] = UNSET,
    names: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListDeploymentsSortsItem]] = UNSET,
) -> Optional[Union[DeploymentsPaginated, Error]]:
    """List Deployments

     List Deployments in an Organization.

    Args:
        organization_id (str):
        deployment_ids (Union[Unset, list[str]]):
        names (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListDeploymentsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeploymentsPaginated, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        deployment_ids=deployment_ids,
        names=names,
        workspace_ids=workspace_ids,
        offset=offset,
        limit=limit,
        sorts=sorts,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    names: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListDeploymentsSortsItem]] = UNSET,
) -> Response[Union[DeploymentsPaginated, Error]]:
    """List Deployments

     List Deployments in an Organization.

    Args:
        organization_id (str):
        deployment_ids (Union[Unset, list[str]]):
        names (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListDeploymentsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeploymentsPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        deployment_ids=deployment_ids,
        names=names,
        workspace_ids=workspace_ids,
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
    deployment_ids: Union[Unset, list[str]] = UNSET,
    names: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListDeploymentsSortsItem]] = UNSET,
) -> Optional[Union[DeploymentsPaginated, Error]]:
    """List Deployments

     List Deployments in an Organization.

    Args:
        organization_id (str):
        deployment_ids (Union[Unset, list[str]]):
        names (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListDeploymentsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeploymentsPaginated, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            deployment_ids=deployment_ids,
            names=names,
            workspace_ids=workspace_ids,
            offset=offset,
            limit=limit,
            sorts=sorts,
        )
    ).parsed
