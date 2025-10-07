"""Update metadata on the collection"""
from http import HTTPStatus
from typing import Any
from typing import cast
from typing import Dict
from typing import Union

import httpx

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.server_error import ServerError
from ...models.update_collection import UpdateCollection
from ...types import Response


def _get_kwargs(
    collection_id: str,
    *,
    body: UpdateCollection,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "patch",
        "url": "/collections/{collection_id}/LIVE".format(
            collection_id=collection_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Any, ServerError]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, {"attribute": "None", "return_type": "None"})
        return response_204
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ServerError.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ServerError.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ServerError.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
        response_415 = ServerError.from_dict(response.json())

        return response_415
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ServerError.from_dict(response.json())

        return response_500

    raise errors.UnexpectedStatus(response.status_code, response.content)


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ServerError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateCollection,
) -> Response[Union[Any, ServerError]]:
    """Update metadata on the collection

    Update the collection's metadata, leaving unspecified fields as-is.

    This method currently operates the same as the corresponding
    PUT method. It may be deprecated in the future, or implemented
    according to the JSON Patch standard.

    Args:
        collection_id (str):
        body (UpdateCollection): Update core collection properties

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateCollection,
) -> Union[Any]:
    """Update metadata on the collection

    Update the collection's metadata, leaving unspecified fields as-is.

    This method currently operates the same as the corresponding
    PUT method. It may be deprecated in the future, or implemented
    according to the JSON Patch standard.

    Args:
        collection_id (str):
        body (UpdateCollection): Update core collection properties

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
    """

    response = sync_detailed(
        collection_id=collection_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed


async def asyncio_detailed(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateCollection,
) -> Response[Union[Any, ServerError]]:
    """Update metadata on the collection

    Update the collection's metadata, leaving unspecified fields as-is.

    This method currently operates the same as the corresponding
    PUT method. It may be deprecated in the future, or implemented
    according to the JSON Patch standard.

    Args:
        collection_id (str):
        body (UpdateCollection): Update core collection properties

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ServerError]]
    """

    kwargs = _get_kwargs(
        collection_id=collection_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collection_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateCollection,
) -> Union[Any]:
    """Update metadata on the collection

    Update the collection's metadata, leaving unspecified fields as-is.

    This method currently operates the same as the corresponding
    PUT method. It may be deprecated in the future, or implemented
    according to the JSON Patch standard.

    Args:
        collection_id (str):
        body (UpdateCollection): Update core collection properties

    Raises:
        errors.UnexpectedStatus: If the server returns a status code greater than or equal to 300.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any]
    """

    response = await asyncio_detailed(
        collection_id=collection_id,
        client=client,
        body=body,
    )
    if isinstance(response.parsed, ServerError):
        raise errors.UnexpectedStatus(response.status_code, response.content)

    return response.parsed
