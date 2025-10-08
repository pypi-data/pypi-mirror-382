"""General utility functions.

This submodule provides various utility functions and decorators used
throughout the package.

Includes:
    connected: Decorator to require a connected client.
    authenticated: Decorator to require an authenticated account.
    consented: Decorator to require an opted-in account.
    dump: Serialize a Pydantic model for storage or transmission.
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

import pydantic_core
from pydantic import BaseModel

from .errors import (
    ClientMissingError,
    NotAuthenticatedError,
    NotConnectedError,
    NotOptedInError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .client import Client


logger: logging.Logger = logging.getLogger(__name__)


__all__: list[str] = [
    "authenticated",
    "connected",
    "consented",
    "dump",
]


def extract_client(*args: Any, **kwargs: Any) -> Client:
    """Extract the client instance from positional or keyword arguments.

    Assumes the first argument with client-like attributes or an explicit
    'client' keyword argument. Raises AttributeError if no candidate found.
    """
    for arg in args:
        if (
            hasattr(arg, "is_none")
            and hasattr(arg, "is_auth")
            and hasattr(arg, "is_opted_in")
        ):
            return cast("Client", arg)
    if "client" in kwargs:
        return cast("Client", kwargs["client"])
    if hasattr(args[0], "client"):
        return cast("Client", getattr(args[0], "client"))
    raise ClientMissingError(message="Client not found in arguments.")


def connected[**Params, Return](
    func: Callable[Params, Return],
) -> Callable[Params, Return]:
    """Require client connection.

    Inspects `Client` object and raises a :class:`NotConnectedError` if it is
    not connected (`client.is_none` is `True`).

    Args:
        func (Callable[Params, Return]): The function to decorate.

    Returns:
        out (Callable[Params, Return]): The wrapped function, which will raise
            :class:`NotConnectedError` if the client is not connected.

    """

    @wraps(func)
    def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Return:
        client = extract_client(*args, **kwargs)
        logger.debug(
            "Verifying client connection for function '%s'. "
            "Identified function's client parameter of type '%s'.",
            func.__name__,
            type(client),
        )
        if client.is_none:
            msg = f"Connection required for {func.__name__}()"
            logger.error(msg)
            raise NotConnectedError(msg)
        return func(*args, **kwargs)

    return wrapper


def authenticated[**Params, Return](
    func: Callable[Params, Return],
) -> Callable[Params, Return]:
    """Require account authentication.

    Inspects `Client` object and raises a :class:`NotAuthenticatedError` if the
    underlying user account is not authenticated (`client.is_auth` is False).

    Args:
        func (Callable[Params, Return]): The function to decorate.

    Returns:
        out (Callable[Params, Return]): The wrapped function, which will raise
            :class:`NotAuthenticatedError` if the account is not authenticated.

    """

    @wraps(func)
    def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Return:
        client = extract_client(*args, **kwargs)
        logger.debug(
            "Verifying account authentication for function '%s'. "
            "Identified function's client parameter of type '%s'.",
            func.__name__,
            type(client),
        )
        if not client.is_auth:
            msg = f"Authentication required for {func.__name__}()"
            logger.error(msg)
            raise NotAuthenticatedError(msg)
        return func(*args, **kwargs)

    return wrapper


def consented[**Params, Return](
    func: Callable[Params, Return],
) -> Callable[Params, Return]:
    """Require account opt-in.

    Inspects `Client` object and raises a :class:`NotOptedInError` if the
    underlying user account is not opted in (`client.is_opted_in` is False).

    Args:
        func (Callable[Params, Return]): The function to decorate.

    Returns:
        out (Callable[Params, Return]): The wrapped function, which will raise
            :class:`NotOptedInError` if the account is not opted in.

    """

    @wraps(func)
    def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Return:
        client = extract_client(*args, **kwargs)
        logger.debug(
            "Verifying whether account has opted in for function '%s'. "
            "Identified function's client parameter of type '%s'.",
            func.__name__,
            type(client),
        )
        if not client.is_opted_in:
            msg = f"Opt-in required for {func.__name__}()"
            logger.error(msg)
            raise NotOptedInError(msg)
        return func(*args, **kwargs)

    return wrapper


def dump(**kwargs: Any) -> Callable:
    """Serialize a Pydantic model for storage or transmission."""

    def base_encoder(obj: object) -> dict:
        """Encode models and objects for serialization."""
        if isinstance(obj, BaseModel):
            return obj.model_dump(**kwargs)
        return pydantic_core.to_jsonable_python(obj)

    return base_encoder
