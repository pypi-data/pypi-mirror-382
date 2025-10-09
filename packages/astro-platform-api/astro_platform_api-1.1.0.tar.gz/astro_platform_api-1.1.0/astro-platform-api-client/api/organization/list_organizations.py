from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_organizations_astronomer_product import ListOrganizationsAstronomerProduct
from ...models.list_organizations_product import ListOrganizationsProduct
from ...models.list_organizations_product_plan import ListOrganizationsProductPlan
from ...models.list_organizations_sorts_item import ListOrganizationsSortsItem
from ...models.list_organizations_support_plan import ListOrganizationsSupportPlan
from ...models.organizations_paginated import OrganizationsPaginated
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    support_plan: Union[Unset, ListOrganizationsSupportPlan] = UNSET,
    product_plan: Union[Unset, ListOrganizationsProductPlan] = UNSET,
    astronomer_product: Union[Unset, ListOrganizationsAstronomerProduct] = UNSET,
    product: Union[Unset, ListOrganizationsProduct] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListOrganizationsSortsItem]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_support_plan: Union[Unset, str] = UNSET
    if not isinstance(support_plan, Unset):
        json_support_plan = support_plan.value

    params["supportPlan"] = json_support_plan

    json_product_plan: Union[Unset, str] = UNSET
    if not isinstance(product_plan, Unset):
        json_product_plan = product_plan.value

    params["productPlan"] = json_product_plan

    json_astronomer_product: Union[Unset, str] = UNSET
    if not isinstance(astronomer_product, Unset):
        json_astronomer_product = astronomer_product.value

    params["astronomerProduct"] = json_astronomer_product

    json_product: Union[Unset, str] = UNSET
    if not isinstance(product, Unset):
        json_product = product.value

    params["product"] = json_product

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
        "url": "/organizations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, OrganizationsPaginated]]:
    if response.status_code == 200:
        response_200 = OrganizationsPaginated.from_dict(response.json())

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
) -> Response[Union[Error, OrganizationsPaginated]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    support_plan: Union[Unset, ListOrganizationsSupportPlan] = UNSET,
    product_plan: Union[Unset, ListOrganizationsProductPlan] = UNSET,
    astronomer_product: Union[Unset, ListOrganizationsAstronomerProduct] = UNSET,
    product: Union[Unset, ListOrganizationsProduct] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListOrganizationsSortsItem]] = UNSET,
) -> Response[Union[Error, OrganizationsPaginated]]:
    """List Organizations

     List the details about all Organizations that you have access to. Requires using a personal access
    token (PAT) for authentication.

    Args:
        support_plan (Union[Unset, ListOrganizationsSupportPlan]):
        product_plan (Union[Unset, ListOrganizationsProductPlan]):
        astronomer_product (Union[Unset, ListOrganizationsAstronomerProduct]):
        product (Union[Unset, ListOrganizationsProduct]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListOrganizationsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, OrganizationsPaginated]]
    """

    kwargs = _get_kwargs(
        support_plan=support_plan,
        product_plan=product_plan,
        astronomer_product=astronomer_product,
        product=product,
        offset=offset,
        limit=limit,
        sorts=sorts,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    support_plan: Union[Unset, ListOrganizationsSupportPlan] = UNSET,
    product_plan: Union[Unset, ListOrganizationsProductPlan] = UNSET,
    astronomer_product: Union[Unset, ListOrganizationsAstronomerProduct] = UNSET,
    product: Union[Unset, ListOrganizationsProduct] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListOrganizationsSortsItem]] = UNSET,
) -> Optional[Union[Error, OrganizationsPaginated]]:
    """List Organizations

     List the details about all Organizations that you have access to. Requires using a personal access
    token (PAT) for authentication.

    Args:
        support_plan (Union[Unset, ListOrganizationsSupportPlan]):
        product_plan (Union[Unset, ListOrganizationsProductPlan]):
        astronomer_product (Union[Unset, ListOrganizationsAstronomerProduct]):
        product (Union[Unset, ListOrganizationsProduct]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListOrganizationsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, OrganizationsPaginated]
    """

    return sync_detailed(
        client=client,
        support_plan=support_plan,
        product_plan=product_plan,
        astronomer_product=astronomer_product,
        product=product,
        offset=offset,
        limit=limit,
        sorts=sorts,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    support_plan: Union[Unset, ListOrganizationsSupportPlan] = UNSET,
    product_plan: Union[Unset, ListOrganizationsProductPlan] = UNSET,
    astronomer_product: Union[Unset, ListOrganizationsAstronomerProduct] = UNSET,
    product: Union[Unset, ListOrganizationsProduct] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListOrganizationsSortsItem]] = UNSET,
) -> Response[Union[Error, OrganizationsPaginated]]:
    """List Organizations

     List the details about all Organizations that you have access to. Requires using a personal access
    token (PAT) for authentication.

    Args:
        support_plan (Union[Unset, ListOrganizationsSupportPlan]):
        product_plan (Union[Unset, ListOrganizationsProductPlan]):
        astronomer_product (Union[Unset, ListOrganizationsAstronomerProduct]):
        product (Union[Unset, ListOrganizationsProduct]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListOrganizationsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, OrganizationsPaginated]]
    """

    kwargs = _get_kwargs(
        support_plan=support_plan,
        product_plan=product_plan,
        astronomer_product=astronomer_product,
        product=product,
        offset=offset,
        limit=limit,
        sorts=sorts,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    support_plan: Union[Unset, ListOrganizationsSupportPlan] = UNSET,
    product_plan: Union[Unset, ListOrganizationsProductPlan] = UNSET,
    astronomer_product: Union[Unset, ListOrganizationsAstronomerProduct] = UNSET,
    product: Union[Unset, ListOrganizationsProduct] = UNSET,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 20,
    sorts: Union[Unset, list[ListOrganizationsSortsItem]] = UNSET,
) -> Optional[Union[Error, OrganizationsPaginated]]:
    """List Organizations

     List the details about all Organizations that you have access to. Requires using a personal access
    token (PAT) for authentication.

    Args:
        support_plan (Union[Unset, ListOrganizationsSupportPlan]):
        product_plan (Union[Unset, ListOrganizationsProductPlan]):
        astronomer_product (Union[Unset, ListOrganizationsAstronomerProduct]):
        product (Union[Unset, ListOrganizationsProduct]):
        offset (Union[Unset, int]):  Default: 0.
        limit (Union[Unset, int]):  Default: 20.
        sorts (Union[Unset, list[ListOrganizationsSortsItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, OrganizationsPaginated]
    """

    return (
        await asyncio_detailed(
            client=client,
            support_plan=support_plan,
            product_plan=product_plan,
            astronomer_product=astronomer_product,
            product=product,
            offset=offset,
            limit=limit,
            sorts=sorts,
        )
    ).parsed
