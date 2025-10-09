from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment_options import DeploymentOptions
from ...models.error import Error
from ...models.get_deployment_options_cloud_provider import GetDeploymentOptionsCloudProvider
from ...models.get_deployment_options_deployment_type import GetDeploymentOptionsDeploymentType
from ...models.get_deployment_options_executor import GetDeploymentOptionsExecutor
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    deployment_id: Union[Unset, str] = UNSET,
    deployment_type: Union[Unset, GetDeploymentOptionsDeploymentType] = UNSET,
    executor: Union[Unset, GetDeploymentOptionsExecutor] = UNSET,
    cloud_provider: Union[Unset, GetDeploymentOptionsCloudProvider] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["deploymentId"] = deployment_id

    json_deployment_type: Union[Unset, str] = UNSET
    if not isinstance(deployment_type, Unset):
        json_deployment_type = deployment_type.value

    params["deploymentType"] = json_deployment_type

    json_executor: Union[Unset, str] = UNSET
    if not isinstance(executor, Unset):
        json_executor = executor.value

    params["executor"] = json_executor

    json_cloud_provider: Union[Unset, str] = UNSET
    if not isinstance(cloud_provider, Unset):
        json_cloud_provider = cloud_provider.value

    params["cloudProvider"] = json_cloud_provider

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/organizations/{organization_id}/deployment-options",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DeploymentOptions, Error]]:
    if response.status_code == 200:
        response_200 = DeploymentOptions.from_dict(response.json())

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
) -> Response[Union[DeploymentOptions, Error]]:
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
    deployment_id: Union[Unset, str] = UNSET,
    deployment_type: Union[Unset, GetDeploymentOptionsDeploymentType] = UNSET,
    executor: Union[Unset, GetDeploymentOptionsExecutor] = UNSET,
    cloud_provider: Union[Unset, GetDeploymentOptionsCloudProvider] = UNSET,
) -> Response[Union[DeploymentOptions, Error]]:
    """Get Deployment options

     Get the options available for configuring a Deployment.

    Args:
        organization_id (str):
        deployment_id (Union[Unset, str]):
        deployment_type (Union[Unset, GetDeploymentOptionsDeploymentType]):
        executor (Union[Unset, GetDeploymentOptionsExecutor]):
        cloud_provider (Union[Unset, GetDeploymentOptionsCloudProvider]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeploymentOptions, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        deployment_id=deployment_id,
        deployment_type=deployment_type,
        executor=executor,
        cloud_provider=cloud_provider,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    deployment_id: Union[Unset, str] = UNSET,
    deployment_type: Union[Unset, GetDeploymentOptionsDeploymentType] = UNSET,
    executor: Union[Unset, GetDeploymentOptionsExecutor] = UNSET,
    cloud_provider: Union[Unset, GetDeploymentOptionsCloudProvider] = UNSET,
) -> Optional[Union[DeploymentOptions, Error]]:
    """Get Deployment options

     Get the options available for configuring a Deployment.

    Args:
        organization_id (str):
        deployment_id (Union[Unset, str]):
        deployment_type (Union[Unset, GetDeploymentOptionsDeploymentType]):
        executor (Union[Unset, GetDeploymentOptionsExecutor]):
        cloud_provider (Union[Unset, GetDeploymentOptionsCloudProvider]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeploymentOptions, Error]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        deployment_id=deployment_id,
        deployment_type=deployment_type,
        executor=executor,
        cloud_provider=cloud_provider,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    deployment_id: Union[Unset, str] = UNSET,
    deployment_type: Union[Unset, GetDeploymentOptionsDeploymentType] = UNSET,
    executor: Union[Unset, GetDeploymentOptionsExecutor] = UNSET,
    cloud_provider: Union[Unset, GetDeploymentOptionsCloudProvider] = UNSET,
) -> Response[Union[DeploymentOptions, Error]]:
    """Get Deployment options

     Get the options available for configuring a Deployment.

    Args:
        organization_id (str):
        deployment_id (Union[Unset, str]):
        deployment_type (Union[Unset, GetDeploymentOptionsDeploymentType]):
        executor (Union[Unset, GetDeploymentOptionsExecutor]):
        cloud_provider (Union[Unset, GetDeploymentOptionsCloudProvider]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeploymentOptions, Error]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        deployment_id=deployment_id,
        deployment_type=deployment_type,
        executor=executor,
        cloud_provider=cloud_provider,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient,
    deployment_id: Union[Unset, str] = UNSET,
    deployment_type: Union[Unset, GetDeploymentOptionsDeploymentType] = UNSET,
    executor: Union[Unset, GetDeploymentOptionsExecutor] = UNSET,
    cloud_provider: Union[Unset, GetDeploymentOptionsCloudProvider] = UNSET,
) -> Optional[Union[DeploymentOptions, Error]]:
    """Get Deployment options

     Get the options available for configuring a Deployment.

    Args:
        organization_id (str):
        deployment_id (Union[Unset, str]):
        deployment_type (Union[Unset, GetDeploymentOptionsDeploymentType]):
        executor (Union[Unset, GetDeploymentOptionsExecutor]):
        cloud_provider (Union[Unset, GetDeploymentOptionsCloudProvider]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeploymentOptions, Error]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            deployment_id=deployment_id,
            deployment_type=deployment_type,
            executor=executor,
            cloud_provider=cloud_provider,
        )
    ).parsed
