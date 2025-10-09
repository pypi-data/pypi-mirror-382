from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.environment_objects_paginated import EnvironmentObjectsPaginated
from ...models.error import Error
from ...models.list_environment_objects_object_type import ListEnvironmentObjectsObjectType
from ...models.list_environment_objects_sorts_item import ListEnvironmentObjectsSortsItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListEnvironmentObjectsSortsItem]] = UNSET,
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    object_type: Union[Unset, ListEnvironmentObjectsObjectType] = UNSET,
    object_key: Union[Unset, str] = UNSET,
    show_secrets: Union[Unset, bool] = UNSET,
    resolve_linked: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    json_sorts: Union[Unset, list[str]] = UNSET
    if not isinstance(sorts, Unset):
        json_sorts = []
        for sorts_item_data in sorts:
            sorts_item = sorts_item_data.value
            json_sorts.append(sorts_item)

    params["sorts"] = json_sorts

    params["workspaceId"] = workspace_id

    params["deploymentId"] = deployment_id

    json_object_type: Union[Unset, str] = UNSET
    if not isinstance(object_type, Unset):
        json_object_type = object_type.value

    params["objectType"] = json_object_type

    params["objectKey"] = object_key

    params["showSecrets"] = show_secrets

    params["resolveLinked"] = resolve_linked

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/environment-objects",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[EnvironmentObjectsPaginated, Error]]:
    if response.status_code == 200:
        response_200 = EnvironmentObjectsPaginated.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 405:
        response_405 = Error.from_dict(response.json())

        return response_405

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[EnvironmentObjectsPaginated, Error]]:
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
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListEnvironmentObjectsSortsItem]] = UNSET,
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    object_type: Union[Unset, ListEnvironmentObjectsObjectType] = UNSET,
    object_key: Union[Unset, str] = UNSET,
    show_secrets: Union[Unset, bool] = UNSET,
    resolve_linked: Union[Unset, bool] = UNSET,
) -> Response[Union[EnvironmentObjectsPaginated, Error]]:
    """List environment objects

     List environment objects in a Workspace or Deployment.

    Args:
        organization_id (str):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListEnvironmentObjectsSortsItem]]):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        object_type (Union[Unset, ListEnvironmentObjectsObjectType]):
        object_key (Union[Unset, str]):
        show_secrets (Union[Unset, bool]):
        resolve_linked (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EnvironmentObjectsPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        offset=offset,
        limit=limit,
        sorts=sorts,
        workspace_id=workspace_id,
        deployment_id=deployment_id,
        object_type=object_type,
        object_key=object_key,
        show_secrets=show_secrets,
        resolve_linked=resolve_linked,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListEnvironmentObjectsSortsItem]] = UNSET,
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    object_type: Union[Unset, ListEnvironmentObjectsObjectType] = UNSET,
    object_key: Union[Unset, str] = UNSET,
    show_secrets: Union[Unset, bool] = UNSET,
    resolve_linked: Union[Unset, bool] = UNSET,
) -> Optional[Union[EnvironmentObjectsPaginated, Error]]:
    """List environment objects

     List environment objects in a Workspace or Deployment.

    Args:
        organization_id (str):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListEnvironmentObjectsSortsItem]]):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        object_type (Union[Unset, ListEnvironmentObjectsObjectType]):
        object_key (Union[Unset, str]):
        show_secrets (Union[Unset, bool]):
        resolve_linked (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EnvironmentObjectsPaginated, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        offset=offset,
        limit=limit,
        sorts=sorts,
        workspace_id=workspace_id,
        deployment_id=deployment_id,
        object_type=object_type,
        object_key=object_key,
        show_secrets=show_secrets,
        resolve_linked=resolve_linked,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListEnvironmentObjectsSortsItem]] = UNSET,
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    object_type: Union[Unset, ListEnvironmentObjectsObjectType] = UNSET,
    object_key: Union[Unset, str] = UNSET,
    show_secrets: Union[Unset, bool] = UNSET,
    resolve_linked: Union[Unset, bool] = UNSET,
) -> Response[Union[EnvironmentObjectsPaginated, Error]]:
    """List environment objects

     List environment objects in a Workspace or Deployment.

    Args:
        organization_id (str):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListEnvironmentObjectsSortsItem]]):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        object_type (Union[Unset, ListEnvironmentObjectsObjectType]):
        object_key (Union[Unset, str]):
        show_secrets (Union[Unset, bool]):
        resolve_linked (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[EnvironmentObjectsPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        offset=offset,
        limit=limit,
        sorts=sorts,
        workspace_id=workspace_id,
        deployment_id=deployment_id,
        object_type=object_type,
        object_key=object_key,
        show_secrets=show_secrets,
        resolve_linked=resolve_linked,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListEnvironmentObjectsSortsItem]] = UNSET,
    workspace_id: Union[Unset, str] = UNSET,
    deployment_id: Union[Unset, str] = UNSET,
    object_type: Union[Unset, ListEnvironmentObjectsObjectType] = UNSET,
    object_key: Union[Unset, str] = UNSET,
    show_secrets: Union[Unset, bool] = UNSET,
    resolve_linked: Union[Unset, bool] = UNSET,
) -> Optional[Union[EnvironmentObjectsPaginated, Error]]:
    """List environment objects

     List environment objects in a Workspace or Deployment.

    Args:
        organization_id (str):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListEnvironmentObjectsSortsItem]]):
        workspace_id (Union[Unset, str]):
        deployment_id (Union[Unset, str]):
        object_type (Union[Unset, ListEnvironmentObjectsObjectType]):
        object_key (Union[Unset, str]):
        show_secrets (Union[Unset, bool]):
        resolve_linked (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[EnvironmentObjectsPaginated, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            offset=offset,
            limit=limit,
            sorts=sorts,
            workspace_id=workspace_id,
            deployment_id=deployment_id,
            object_type=object_type,
            object_key=object_key,
            show_secrets=show_secrets,
            resolve_linked=resolve_linked,
        )
    ).parsed
