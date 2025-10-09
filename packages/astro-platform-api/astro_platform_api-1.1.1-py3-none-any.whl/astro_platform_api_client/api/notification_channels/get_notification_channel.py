from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.notification_channel import NotificationChannel
from ...types import Response


def _get_kwargs(
    organization_id: str,
    notification_channel_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/notification-channels/{notification_channel_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, NotificationChannel]]:
    if response.status_code == 200:
        response_200 = NotificationChannel.from_dict(response.json())

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
) -> Response[Union[Error, NotificationChannel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    notification_channel_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Error, NotificationChannel]]:
    """Get an Alert Notification Channel

     Get an Alert Notification Channel.

    Args:
        organization_id (str):
        notification_channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, NotificationChannel]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        notification_channel_id=notification_channel_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    notification_channel_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Error, NotificationChannel]]:
    """Get an Alert Notification Channel

     Get an Alert Notification Channel.

    Args:
        organization_id (str):
        notification_channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, NotificationChannel]
    """

    return sync_detailed(
        organization_id=organization_id,
        notification_channel_id=notification_channel_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    notification_channel_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Error, NotificationChannel]]:
    """Get an Alert Notification Channel

     Get an Alert Notification Channel.

    Args:
        organization_id (str):
        notification_channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, NotificationChannel]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        notification_channel_id=notification_channel_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    notification_channel_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Error, NotificationChannel]]:
    """Get an Alert Notification Channel

     Get an Alert Notification Channel.

    Args:
        organization_id (str):
        notification_channel_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, NotificationChannel]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            notification_channel_id=notification_channel_id,
            client=client,
        )
    ).parsed
