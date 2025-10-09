import datetime
from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_start_date: Union[Unset, str] = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["startDate"] = json_start_date

    json_end_date: Union[Unset, str] = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["endDate"] = json_end_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/audit-logs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, list[int]]]:
    if response.status_code == 200:
        response_200 = cast(list[int], response.content)

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.content)

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.content)

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.content)

        return response_403

    if response.status_code == 500:
        response_500 = Error.from_dict(response.content)

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, list[int]]]:
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
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[Union[Error, list[int]]]:
    """Get Organization audit logs

     Retrieve logs across a specified time period for an Organization.

    Args:
        organization_id (str):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list[int]]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        start_date=start_date,
        end_date=end_date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[Union[Error, list[int]]]:
    """Get Organization audit logs

     Retrieve logs across a specified time period for an Organization.

    Args:
        organization_id (str):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list[int]]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        start_date=start_date,
        end_date=end_date,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[Union[Error, list[int]]]:
    """Get Organization audit logs

     Retrieve logs across a specified time period for an Organization.

    Args:
        organization_id (str):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list[int]]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        start_date=start_date,
        end_date=end_date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    start_date: Union[Unset, datetime.datetime] = UNSET,
    end_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[Union[Error, list[int]]]:
    """Get Organization audit logs

     Retrieve logs across a specified time period for an Organization.

    Args:
        organization_id (str):
        start_date (Union[Unset, datetime.datetime]):
        end_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list[int]]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            start_date=start_date,
            end_date=end_date,
        )
    ).parsed
