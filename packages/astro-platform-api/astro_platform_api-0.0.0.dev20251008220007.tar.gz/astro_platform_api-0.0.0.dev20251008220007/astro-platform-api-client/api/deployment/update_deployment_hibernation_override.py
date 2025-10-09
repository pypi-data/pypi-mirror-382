from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment_hibernation_override import DeploymentHibernationOverride
from ...models.error import Error
from ...models.override_deployment_hibernation_body import OverrideDeploymentHibernationBody
from ...types import Response


def _get_kwargs(
    organization_id: str,
    deployment_id: str,
    *,
    body: OverrideDeploymentHibernationBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/organizations/{organization_id}/deployments/{deployment_id}/hibernation-override",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DeploymentHibernationOverride, Error]]:
    if response.status_code == 200:
        response_200 = DeploymentHibernationOverride.from_dict(response.json())

        return response_200

    if 400 <= response.status_code <= 499:
        response_4xx = Error.from_dict(response.json())

        return response_4xx

    if 500 <= response.status_code <= 599:
        response_5xx = Error.from_dict(response.json())

        return response_5xx

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[DeploymentHibernationOverride, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    deployment_id: str,
    *,
    client: AuthenticatedClient,
    body: OverrideDeploymentHibernationBody,
) -> Response[Union[DeploymentHibernationOverride, Error]]:
    """Configure a hibernation override for a deployment

    Args:
        organization_id (str):
        deployment_id (str):
        body (OverrideDeploymentHibernationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeploymentHibernationOverride, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        deployment_id=deployment_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    deployment_id: str,
    *,
    client: AuthenticatedClient,
    body: OverrideDeploymentHibernationBody,
) -> Optional[Union[DeploymentHibernationOverride, Error]]:
    """Configure a hibernation override for a deployment

    Args:
        organization_id (str):
        deployment_id (str):
        body (OverrideDeploymentHibernationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeploymentHibernationOverride, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        deployment_id=deployment_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    deployment_id: str,
    *,
    client: AuthenticatedClient,
    body: OverrideDeploymentHibernationBody,
) -> Response[Union[DeploymentHibernationOverride, Error]]:
    """Configure a hibernation override for a deployment

    Args:
        organization_id (str):
        deployment_id (str):
        body (OverrideDeploymentHibernationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeploymentHibernationOverride, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        deployment_id=deployment_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    deployment_id: str,
    *,
    client: AuthenticatedClient,
    body: OverrideDeploymentHibernationBody,
) -> Optional[Union[DeploymentHibernationOverride, Error]]:
    """Configure a hibernation override for a deployment

    Args:
        organization_id (str):
        deployment_id (str):
        body (OverrideDeploymentHibernationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeploymentHibernationOverride, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            deployment_id=deployment_id,
            client=client,
            body=body,
        )
    ).parsed
