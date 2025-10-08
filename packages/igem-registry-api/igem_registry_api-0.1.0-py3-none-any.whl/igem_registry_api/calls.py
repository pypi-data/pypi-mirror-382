"""Core request execution and error handling.

This submodule provides the central request pipeline for single and paginated
API calls, including unified error handling, retry and backoff, rate-limit
awareness, and optional response validation with Pydantic models.

Exports:
    PaginatedResponse: Model representing a paginated API response.
    call: Executes a single HTTP request with retries and optional parsing.
    call_paginated: Iterates page-based endpoints and aggregates results.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from http import HTTPStatus
from time import sleep
from typing import TYPE_CHECKING, Annotated, overload

from pydantic import BaseModel, Field, ValidationError

from .__meta__ import __repository__, __title__, __version__
from .errors import (
    EmptyBodyError,
    HTTPError,
    ResponseValidationError,
    RetryExhaustedError,
    TransportError,
)
from .rates import cooldown, ratelimit
from .schemas import LockedModel, Progress

if TYPE_CHECKING:
    from pydantic import NonNegativeInt
    from requests import Request

    from .client import Client


logger: logging.Logger = logging.getLogger(__name__)


__all__: list[str] = [
    "PaginatedResponse",
    "call",
    "call_paginated",
]


class PaginatedResponse[
    DataObject: BaseModel,
    MetaObject: BaseModel | Iterable[BaseModel] | None,
](
    LockedModel,
):
    """Page-based API response.

    Represents a paginated response from the Registry API and includes the
    data items, total item count, current page number, and optional response
    metadata.

    Attributes:
        data (list[DataObject]): Data objects returned in the response.
        page (int): Current page number.
        total (int): Total number of objects available.
        meta (MetaObject | None): Additional metadata about the response.

    """

    data: Annotated[
        list[DataObject],
        Field(
            title="Data",
            description="List of data objects returned in the response.",
            min_length=0,
            max_length=100,
        ),
    ]

    page: Annotated[
        int,
        Field(
            title="Page",
            description="Current page number.",
            ge=1,
        ),
    ]

    total: Annotated[
        int,
        Field(
            title="Total",
            description="Total number of objects available.",
            ge=0,
        ),
    ]

    meta: Annotated[
        MetaObject | None,
        Field(
            title="Metadata",
            description="Additional metadata about the response.",
            alias="metadata",
        ),
    ] = None


@overload
def call(
    client: Client,
    request: Request,
    data: None = None,
) -> None: ...


@overload
def call[DataObject: BaseModel](
    client: Client,
    request: Request,
    data: type[DataObject],
) -> DataObject: ...


def call(
    client,
    request,
    data=None,
):
    """Execute a single API call.

    This function prepares and dispatches a `requests.Request` using the
    provided `Client` session. It implements retry logic, rate-limit awareness,
    and optional Pydantic model validation of the response body.

    Behavior:
    - Ensures a default `User-Agent` based on the library's metadata.
    - Prepares the HTTP request from `requests.Request`.
    - Applies a pre-request cooldown delay (`client.cooldown`).
    - Sends the request using the `Client`'s configured `requests.Session`.
    - Retries the request (`client.retries` times) on HTTP 429 (rate limit).
    - Updates the client's rate-limit state (`client.ratelimit`) and
        recalculates `client.cooldown` for the following call.
    - If `data` is provided, attempts to parse and validate the response
        body into an instance of the specified Pydantic model.
    - If `data` is omitted or `client.stream` is enabled, the function
        does not parse the body and instead returns `None`.

    Args:
        client (Client): Registry API client that holds the HTTP session,
            retry configuration, and rate-limit state.
        request (Request): HTTP request definition.
        data (type[DataObject] | None): Model of the response body. When
            provided, function returns a validated instance of this model.
            If omitted, the function returns `None`.

    Returns:
        out (type[DataObject] | None): `None` if no data model is provided or
        streaming is enabled. Otherwise, an instance of the specified model
        containing the validated response data.

    Raises:
        TransportError: If a network or transport-level failure occurs before
            an HTTP response is received.
        RetryExhaustedError: If the request fails after exhausting all retry
            attempts.
        HTTPError: If the server responds with an unexpected non-success HTTP
            status.
        EmptyBodyError: If a response is received without content when a body
            is required for validation.
        ResponseValidationError: If the response body cannot be parsed or fails
            validation against the specified model.

    Example:
        Check the health status of a Registry instance.

        ```python
        import requests

        from igem_registry_api import Client, HealthCheck, call

        client = Client()
        client.connect()

        request = requests.Request(
            method="GET",
            url=f"{client.base}/health",
        )

        health = call(client, request, HealthCheck)
        ```

    """
    request.headers.setdefault(
        "User-Agent",
        f"{__title__}/{__version__} (+{__repository__})",
    )

    for attempt in range(max(1, client.retries)):
        prepared = client.session.prepare_request(request)
        logger.debug(
            "Prepared '%s' request to '%s' with headers: '%s', body: '%s'.",
            prepared.method,
            prepared.url,
            prepared.headers,
            prepared.body,
        )

        if client.cooldown:
            logger.debug(
                "Cooldown before sending '%s' request to '%s': %s seconds.",
                prepared.method,
                prepared.url,
                client.cooldown,
            )
            sleep(client.cooldown)

        try:
            response = client.session.send(
                request=prepared,
                verify=client.verify,
                timeout=client.timeout,
                stream=client.stream,
                proxies=client.proxies,
                cert=client.certificate,
                allow_redirects=client.redirects,
            )
        except Exception as e:
            raise TransportError(prepared.method, prepared.url, e) from e

        status = HTTPStatus(response.status_code)
        details = {
            "method": prepared.method,
            "url": prepared.url,
            "status": response.status_code,
            "reason": response.reason,
        }

        if status.is_success:
            logger.debug(
                "Response for '%s' request to '%s': %s, %s. "
                "Response headers: %s",
                *details.values(),
                response.headers,
            )
            client.ratelimit = ratelimit(response.headers)
            client.cooldown = cooldown(client.ratelimit)
            break

        if status == HTTPStatus.TOO_MANY_REQUESTS:
            logger.warning(
                "Rate limit exceeded for '%s' request to '%s': %s, %s. "
                "Retrying request (attempt %s of %s).",
                *details.values(),
                attempt + 1,
                client.retries,
            )
            client.ratelimit = ratelimit(response.headers)
            client.cooldown = cooldown(client.ratelimit)
            continue

        raise HTTPError(**details)

    else:
        raise RetryExhaustedError(request.method, request.url, client.retries)

    if data is None or client.stream:
        return None

    if not response.content:
        raise EmptyBodyError(**details)

    try:
        logger.debug(
            "Response content for '%s' request to '%s': %s.",
            request.method,
            request.url,
            response.content[:1000].decode(errors="ignore"),
        )
        return data.model_validate_json(response.content)
    except ValidationError as e:
        raise ResponseValidationError(
            request.method,
            request.url,
            response.content[:1000].decode(errors="ignore"),
            e,
        ) from e


@overload
def call_paginated[
    DataObject: BaseModel,
    MetaObject: BaseModel | Iterable[BaseModel],
](
    client: Client,
    request: Request,
    data: type[DataObject],
    meta: type[MetaObject],
    *,
    limit: NonNegativeInt | None = None,
    progress: Progress | None = None,
) -> tuple[list[DataObject], MetaObject]: ...


@overload
def call_paginated[
    DataObject: BaseModel,
](
    client: Client,
    request: Request,
    data: type[DataObject],
    meta: None = None,
    *,
    limit: NonNegativeInt | None = None,
    progress: Progress | None = None,
) -> tuple[list[DataObject], None]: ...


def call_paginated(
    client,
    request,
    data,
    meta=None,
    *,
    limit=None,
    progress=None,
):
    """Perform a paginated API call.

    This function repeatedly invokes `call()` to fetch successive pages,
    aggregating received items into a single list. Optionally returns typed
    response metadata and reports progress.

    Behavior:
    - Initializes pagination with `page=1` and `pageSize=100` (maximum size).
    - Calls `call()` with `PaginatedResponse[data, meta]` until the total or
        desired (`limit`) item count is reached or an empty page is received.
    - Invokes `progress(current, total)` to report progress when provided.
    - Accumulates and returns all `data` items across pages.
    - Returns response `meta` from the last page if its model is provided.


    Args:
        client (Client): Registry API client that holds the HTTP session,
            retry configuration, and rate-limit state.
        request (Request): HTTP request definition.
        data (type[DataObject] | None): Model of the response data.
        meta (type[MetaObject] | None): Model of the response metadata. When
            provided, function returns a validated instance of this model.
            If omitted, the function returns `None`.
        limit (NonNegativeInt | None): Cap on total items to fetch. If `None`,
            fetches all available.
        progress (Progress | None): Callback function to report progress.

    Returns:
        out (tuple[list[DataObject], MetaObject | None]): A tuple containing
            aggregated data items and, if applicable, the associated metadata.

    Raises:
        TransportError: If a network or transport-level failure occurs before
            an HTTP response is received.
        RetryExhaustedError: If the request fails after exhausting all retry
            attempts.
        HTTPError: If the server responds with an unexpected non-success HTTP
            status.
        EmptyBodyError: If a response is received without content when a body
            is required for validation.
        ResponseValidationError: If the response body cannot be parsed or fails
            validation against the specified model.

    Example:
        Fetch all licenses available in the Registry.

        ```python
        import requests

        from igem_registry_api import Client, License, call_paginated

        client = Client()
        client.connect()

        request = requests.Request(
            method="GET",
            url=f"{client.base}/licenses",
        )

        licenses, _ = call_paginated(client, request, License)
        ```

    """
    results: list = []

    if request.params is None:
        request.params = {}
    request.params["page"] = 1
    request.params["pageSize"] = 100

    logger.debug(
        "Starting pagination for '%s' request to '%s'.",
        request.method,
        request.url,
    )

    while True:
        response = call(
            client,
            request,
            PaginatedResponse[data, meta],
        )

        logger.debug(
            "Received page %s for '%s' request to '%s' with %s items.",
            request.params["page"],
            request.method,
            request.url,
            len(response.data),
        )

        results.extend(response.data)
        if progress:
            progress(current=len(results), total=limit or response.total)

        if len(response.data) == 0 or len(results) >= response.total:
            logger.debug(
                "No more items for '%s' request to '%s' at page %s, "
                "stopping pagination.",
                request.method,
                request.url,
                request.params["page"],
            )
            break

        if limit is not None and len(results) >= limit:
            logger.debug(
                "Reached limit of %s items for '%s' request to '%s', "
                "stopping pagination.",
                limit,
                request.method,
                request.url,
            )
            break

        request.params["page"] += 1

    logger.debug(
        "Final cumulative items: %s.",
        len(results),
    )

    if meta is not None:
        logger.debug(
            "Metadata of the paginated response for '%s' request to '%s': %s",
            request.method,
            request.url,
            response.meta,
        )

    return (
        results[:limit] if limit is not None else results,
        response.meta if meta is not None else None,
    )
