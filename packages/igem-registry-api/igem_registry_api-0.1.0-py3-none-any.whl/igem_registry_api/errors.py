"""Custom exceptions.

This submodule centralizes all error types raised by the package and
normalizes error handling across transport, HTTP, validation, and state
(precondition) failures.

Exports:
    ApiError: Base class for all package errors.
    TransportError: Network failure during request.
    RetryExhaustedError: Exhausted retry budget.
    HTTPError: HTTP response returned non-success status.
    ClientError: 4xx client errors.
    ServerError: 5xx server errors.
    RateLimitError: 429 Too Many Requests.
    EmptyBodyError: Expected a body but response content was empty.
    InputValidationError: Pydantic validation failed for input data.
    ResponseValidationError: Pydantic validation failed for response body.
    ClientConnectionError: Error during client connection process.
    ClientAuthenticationError: Error during client authentication process.
    NotConnectedError: Client is in offline mode.
    NotAuthenticatedError: Client is in anonymous mode.
    NotOptedInError: Account user has not opted in.
    NotFoundError: Resource was not found.

"""

from __future__ import annotations

__all__: list[str] = [
    "ApiError",
    "ClientAuthenticationError",
    "ClientConnectionError",
    "ClientError",
    "EmptyBodyError",
    "HTTPError",
    "InputValidationError",
    "NotAuthenticatedError",
    "NotConnectedError",
    "NotFoundError",
    "NotOptedInError",
    "RateLimitError",
    "ResponseValidationError",
    "RetryExhaustedError",
    "ServerError",
    "TransportError",
]


class ApiError(Exception):
    """Base class for all package errors."""


class TransportError(ApiError):
    """Network failure before an HTTP response is received."""

    def __init__(self, method: str, url: str, error: Exception) -> None:
        """Initialize a transport error.

        Args:
            method (str): HTTP method of the request.
            url (str): Full request URL.
            error (Exception): Underlying exception (e.g. from `requests`).

        """
        self.method = method
        self.url = url
        self.error = error
        super().__init__(
            f"Transport error during '{method}' request to '{url}': {error}",
        )


class RetryExhaustedError(ApiError):
    """Exhausted maximum number of retry attempts."""

    def __init__(self, method: str, url: str, retries: int) -> None:
        """Initialize a retry exhaustion error.

        Args:
            method (str): HTTP method of the request.
            url (str): Full request URL.
            retries (int): Number of retry attempts made.

        """
        self.method = method
        self.url = url
        self.retries = retries
        super().__init__(
            f"Retries exhausted for '{method}' request to '{url}': "
            f"{retries} retries.",
        )


class HTTPError(ApiError):
    """HTTP response returned non-success status."""

    def __init__(
        self,
        status: int,
        reason: str,
        method: str | None,
        url: str | None,
    ) -> None:
        """Initialize an HTTP error.

        Args:
            status (int): HTTP status code of the response.
            reason (str): Reason phrase associated with the status code.
            method (str | None): HTTP method used (e.g. "GET").
            url (str | None): Full request URL.

        """
        self.status = status
        self.reason = reason
        self.method = method
        self.url = url
        super().__init__(
            f"Non-success response for '{method}' request to '{url}': "
            f"{status}, {reason}.",
        )


class ClientError(HTTPError):
    """HTTP response returned a 4xx client error."""


class ServerError(HTTPError):
    """HTTP response returned a 5xx server error."""


class RateLimitError(ClientError):
    """HTTP response returned a rate limit error (429 Too Many Requests)."""


class EmptyBodyError(ApiError):
    """Expected a body but response content was empty."""

    def __init__(
        self,
        method: str,
        url: str,
        status: int,
        reason: str,
    ) -> None:
        """Initialize an empty body error.

        Args:
            method (str): HTTP method of the request.
            url (str): Full request URL.
            status (int): HTTP status code.
            reason (str): Reason phrase for the response.

        """
        self.method = method
        self.url = url
        self.status = status
        self.reason = reason
        super().__init__(
            f"Empty response content for '{method}' request to '{url}': "
            f"{status}, {reason}.",
        )


class InputValidationError(ApiError):
    """Pydantic validation failed while processing input data."""

    def __init__(self, error: Exception) -> None:
        """Initialize an input validation error.

        Args:
            error (Exception): Underlying Pydantic validation error.

        """
        self.error = error
        super().__init__(f"Input validation failed: {error}")


class ResponseValidationError(ApiError):
    """Pydantic validation failed while parsing the response body."""

    def __init__(
        self,
        method: str,
        url: str,
        content: str,
        error: Exception,
    ) -> None:
        """Initialize a response validation error.

        Args:
            method (str): HTTP method of the request.
            url (str): Full request URL.
            content (str): Raw response body.
            error (Exception): Underlying Pydantic validation error.

        """
        self.method = method
        self.url = url
        self.content = content
        self.error = error
        super().__init__(
            f"Failed to parse response for '{method}' request to '{url}': "
            f"{content}. Error: {error}",
        )


class ClientConnectionError(ApiError):
    """Error during the client connection process."""

    def __init__(self, message: str) -> None:
        """Initialize a client connection error.

        Args:
            message (str): Description of the failure.

        """
        self.message = message
        super().__init__(message)


class ClientAuthenticationError(ApiError):
    """Error during the account authentication process."""

    def __init__(self, message: str) -> None:
        """Initialize a client authentication error.

        Args:
            message (str): Description of the failure.

        """
        self.message = message
        super().__init__(message)


class ClientMissingError(ApiError):
    """Error during the client lookup process."""

    def __init__(self, message: str) -> None:
        """Initialize a missing client error.

        Args:
            message (str): Description of the failure.

        """
        self.message = message
        super().__init__(message)


class NotConnectedError(ApiError):
    """Operation requires a client in connected mode."""


class NotAuthenticatedError(ApiError):
    """Operation requires a client in authenticated mode."""


class NotOptedInError(ApiError):
    """Operation requires user consent (opt-in)."""


class NotFoundError(Exception):
    """Registry resource could not be resolved by a given key."""

    def __init__(
        self,
        item: str,
        key: str,
        value: str,
    ) -> None:
        """Initialize a not-found error.

        Args:
            item (str): Type of the missing resource (e.g. "license").
            key (str): Lookup key (e.g. "uuid", "slug").
            value (str): Value that failed to resolve.

        """
        self.item = item
        self.key = key
        self.value = value
        super().__init__(f"Unknown {item} {key} '{value}'.")
