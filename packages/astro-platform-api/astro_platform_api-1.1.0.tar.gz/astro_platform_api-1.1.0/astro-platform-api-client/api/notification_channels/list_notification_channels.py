from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_notification_channels_channel_types_item import ListNotificationChannelsChannelTypesItem
from ...models.list_notification_channels_entity_type import ListNotificationChannelsEntityType
from ...models.list_notification_channels_sorts_item import ListNotificationChannelsSortsItem
from ...models.notification_channels_paginated import NotificationChannelsPaginated
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    notification_channel_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    channel_types: Union[Unset, list[ListNotificationChannelsChannelTypesItem]] = UNSET,
    entity_type: Union[Unset, ListNotificationChannelsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListNotificationChannelsSortsItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_notification_channel_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(notification_channel_ids, Unset):
        json_notification_channel_ids = notification_channel_ids

    params["notificationChannelIds"] = json_notification_channel_ids

    json_deployment_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(deployment_ids, Unset):
        json_deployment_ids = deployment_ids

    params["deploymentIds"] = json_deployment_ids

    json_workspace_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(workspace_ids, Unset):
        json_workspace_ids = workspace_ids

    params["workspaceIds"] = json_workspace_ids

    json_channel_types: Union[Unset, list[str]] = UNSET
    if not isinstance(channel_types, Unset):
        json_channel_types = []
        for channel_types_item_data in channel_types:
            channel_types_item = channel_types_item_data.value
            json_channel_types.append(channel_types_item)

    params["channelTypes"] = json_channel_types

    json_entity_type: Union[Unset, str] = UNSET
    if not isinstance(entity_type, Unset):
        json_entity_type = entity_type.value

    params["entityType"] = json_entity_type

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
        "url": f"/organizations/{organization_id}/notification-channels",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, NotificationChannelsPaginated]]:
    if response.status_code == 200:
        response_200 = NotificationChannelsPaginated.from_dict(response.json())

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
) -> Response[Union[Error, NotificationChannelsPaginated]]:
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
    notification_channel_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    channel_types: Union[Unset, list[ListNotificationChannelsChannelTypesItem]] = UNSET,
    entity_type: Union[Unset, ListNotificationChannelsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListNotificationChannelsSortsItem]] = UNSET,
) -> Response[Union[Error, NotificationChannelsPaginated]]:
    """List Alert Notification Channels

     List Alert Notification Channels.

    Args:
        organization_id (str):
        notification_channel_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        channel_types (Union[Unset, list[ListNotificationChannelsChannelTypesItem]]):
        entity_type (Union[Unset, ListNotificationChannelsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListNotificationChannelsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, NotificationChannelsPaginated]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        notification_channel_ids=notification_channel_ids,
        deployment_ids=deployment_ids,
        workspace_ids=workspace_ids,
        channel_types=channel_types,
        entity_type=entity_type,
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
    notification_channel_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    channel_types: Union[Unset, list[ListNotificationChannelsChannelTypesItem]] = UNSET,
    entity_type: Union[Unset, ListNotificationChannelsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListNotificationChannelsSortsItem]] = UNSET,
) -> Optional[Union[Error, NotificationChannelsPaginated]]:
    """List Alert Notification Channels

     List Alert Notification Channels.

    Args:
        organization_id (str):
        notification_channel_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        channel_types (Union[Unset, list[ListNotificationChannelsChannelTypesItem]]):
        entity_type (Union[Unset, ListNotificationChannelsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListNotificationChannelsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, NotificationChannelsPaginated]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        notification_channel_ids=notification_channel_ids,
        deployment_ids=deployment_ids,
        workspace_ids=workspace_ids,
        channel_types=channel_types,
        entity_type=entity_type,
        offset=offset,
        limit=limit,
        sorts=sorts,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    notification_channel_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    channel_types: Union[Unset, list[ListNotificationChannelsChannelTypesItem]] = UNSET,
    entity_type: Union[Unset, ListNotificationChannelsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListNotificationChannelsSortsItem]] = UNSET,
) -> Response[Union[Error, NotificationChannelsPaginated]]:
    """List Alert Notification Channels

     List Alert Notification Channels.

    Args:
        organization_id (str):
        notification_channel_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        channel_types (Union[Unset, list[ListNotificationChannelsChannelTypesItem]]):
        entity_type (Union[Unset, ListNotificationChannelsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListNotificationChannelsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, NotificationChannelsPaginated]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        notification_channel_ids=notification_channel_ids,
        deployment_ids=deployment_ids,
        workspace_ids=workspace_ids,
        channel_types=channel_types,
        entity_type=entity_type,
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
    notification_channel_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    channel_types: Union[Unset, list[ListNotificationChannelsChannelTypesItem]] = UNSET,
    entity_type: Union[Unset, ListNotificationChannelsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListNotificationChannelsSortsItem]] = UNSET,
) -> Optional[Union[Error, NotificationChannelsPaginated]]:
    """List Alert Notification Channels

     List Alert Notification Channels.

    Args:
        organization_id (str):
        notification_channel_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        channel_types (Union[Unset, list[ListNotificationChannelsChannelTypesItem]]):
        entity_type (Union[Unset, ListNotificationChannelsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListNotificationChannelsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, NotificationChannelsPaginated]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            notification_channel_ids=notification_channel_ids,
            deployment_ids=deployment_ids,
            workspace_ids=workspace_ids,
            channel_types=channel_types,
            entity_type=entity_type,
            offset=offset,
            limit=limit,
            sorts=sorts,
        )
    ).parsed
