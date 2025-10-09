from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.alerts_paginated import AlertsPaginated
from ...models.error import Error
from ...models.list_alerts_alert_types_item import ListAlertsAlertTypesItem
from ...models.list_alerts_entity_type import ListAlertsEntityType
from ...models.list_alerts_sorts_item import ListAlertsSortsItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    alert_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    alert_types: Union[Unset, list[ListAlertsAlertTypesItem]] = UNSET,
    entity_type: Union[Unset, ListAlertsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListAlertsSortsItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_alert_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(alert_ids, Unset):
        json_alert_ids = alert_ids

    params["alertIds"] = json_alert_ids

    json_deployment_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(deployment_ids, Unset):
        json_deployment_ids = deployment_ids

    params["deploymentIds"] = json_deployment_ids

    json_workspace_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(workspace_ids, Unset):
        json_workspace_ids = workspace_ids

    params["workspaceIds"] = json_workspace_ids

    json_alert_types: Union[Unset, list[str]] = UNSET
    if not isinstance(alert_types, Unset):
        json_alert_types = []
        for alert_types_item_data in alert_types:
            alert_types_item = alert_types_item_data.value
            json_alert_types.append(alert_types_item)

    params["alertTypes"] = json_alert_types

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
        "url": f"/organizations/{organization_id}/alerts",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AlertsPaginated, Error]]:
    if response.status_code == 200:
        response_200 = AlertsPaginated.from_dict(response.json())

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
) -> Response[Union[AlertsPaginated, Error]]:
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
    alert_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    alert_types: Union[Unset, list[ListAlertsAlertTypesItem]] = UNSET,
    entity_type: Union[Unset, ListAlertsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListAlertsSortsItem]] = UNSET,
) -> Response[Union[AlertsPaginated, Error]]:
    """List alerts

     List alerts.

    Args:
        organization_id (str):
        alert_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        alert_types (Union[Unset, list[ListAlertsAlertTypesItem]]):
        entity_type (Union[Unset, ListAlertsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListAlertsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AlertsPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        alert_ids=alert_ids,
        deployment_ids=deployment_ids,
        workspace_ids=workspace_ids,
        alert_types=alert_types,
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
    alert_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    alert_types: Union[Unset, list[ListAlertsAlertTypesItem]] = UNSET,
    entity_type: Union[Unset, ListAlertsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListAlertsSortsItem]] = UNSET,
) -> Optional[Union[AlertsPaginated, Error]]:
    """List alerts

     List alerts.

    Args:
        organization_id (str):
        alert_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        alert_types (Union[Unset, list[ListAlertsAlertTypesItem]]):
        entity_type (Union[Unset, ListAlertsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListAlertsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AlertsPaginated, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        alert_ids=alert_ids,
        deployment_ids=deployment_ids,
        workspace_ids=workspace_ids,
        alert_types=alert_types,
        entity_type=entity_type,
        offset=offset,
        limit=limit,
        sorts=sorts,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    alert_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    alert_types: Union[Unset, list[ListAlertsAlertTypesItem]] = UNSET,
    entity_type: Union[Unset, ListAlertsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListAlertsSortsItem]] = UNSET,
) -> Response[Union[AlertsPaginated, Error]]:
    """List alerts

     List alerts.

    Args:
        organization_id (str):
        alert_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        alert_types (Union[Unset, list[ListAlertsAlertTypesItem]]):
        entity_type (Union[Unset, ListAlertsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListAlertsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AlertsPaginated, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        alert_ids=alert_ids,
        deployment_ids=deployment_ids,
        workspace_ids=workspace_ids,
        alert_types=alert_types,
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
    alert_ids: Union[Unset, list[str]] = UNSET,
    deployment_ids: Union[Unset, list[str]] = UNSET,
    workspace_ids: Union[Unset, list[str]] = UNSET,
    alert_types: Union[Unset, list[ListAlertsAlertTypesItem]] = UNSET,
    entity_type: Union[Unset, ListAlertsEntityType] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListAlertsSortsItem]] = UNSET,
) -> Optional[Union[AlertsPaginated, Error]]:
    """List alerts

     List alerts.

    Args:
        organization_id (str):
        alert_ids (Union[Unset, list[str]]):
        deployment_ids (Union[Unset, list[str]]):
        workspace_ids (Union[Unset, list[str]]):
        alert_types (Union[Unset, list[ListAlertsAlertTypesItem]]):
        entity_type (Union[Unset, ListAlertsEntityType]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListAlertsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AlertsPaginated, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            alert_ids=alert_ids,
            deployment_ids=deployment_ids,
            workspace_ids=workspace_ids,
            alert_types=alert_types,
            entity_type=entity_type,
            offset=offset,
            limit=limit,
            sorts=sorts,
        )
    ).parsed
