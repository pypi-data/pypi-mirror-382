"""Registry API client.

This submodule defines the `Client` class, the primary programmatic interface
to the iGEM Registry API. It manages connection state, authentication, and
consent-based operations.

Exports:
    Client: Main class for interacting with the Registry API.
    HealthStatus: Model representing the health status of the Registry API.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Literal

import requests
from pydantic import Field, HttpUrl, TypeAdapter, ValidationError

from .calls import call
from .errors import (
    ClientAuthenticationError,
    ClientConnectionError,
    InputValidationError,
)
from .schemas import CleanEnum, LockedModel
from .utils import authenticated, connected

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Self

    from pydantic import NonNegativeInt

    from .account import Account
    from .rates import RateLimit


logger: logging.Logger = logging.getLogger(__name__)


__all__: list[str] = [
    "Client",
    "HealthStatus",
]


class Mode(CleanEnum):
    """API client operation modes.

    Defines the different modes in which the API client can operate.

    Attributes:
        NONE: No authentication or connection.
        ANON: Anonymous mode, no user context.
        AUTH: Authenticated mode, user context available.

    """

    NONE = "NONE"
    ANON = "ANON"
    AUTH = "AUTH"


class StatusInfo(LockedModel):
    """Status information.

    Represents the runtime status of various resources in the iGEM Registry.

    Attributes:
        status (Literal): Status of the resource.

    """

    status: Annotated[
        Literal["up", "down"],
        Field(
            title="Status",
            description="Status of the resource.",
        ),
    ]


class ServerInfo(StatusInfo):
    """Server information.

    Represents the runtime information of the server.

    Attributes:
        environment (Literal): Environment in which the server is running.
        version (str): Version of the server.

    """

    environment: Annotated[
        Literal["production", "staging", "development"],
        Field(
            title="Environment",
            description="Environment in which the server is running.",
        ),
    ]

    version: Annotated[
        str,
        Field(
            title="Version",
            description="Version of the server.",
        ),
    ]


class ResourceData(LockedModel):
    """Resource data.

    Represents the information related to the runtime status of various
    resources in the iGEM Registry.

    Attributes:
        server (ServerInfo | None): Data about the server status.
        database (StatusInfo | None): Data about the database status.
        memory_rss (StatusInfo | None): Data about the memory RSS status.
        redis (StatusInfo | None): Data about the Redis status.

    """

    server: Annotated[
        ServerInfo | None,
        Field(
            title="Server",
            description="Data about the server status.",
        ),
    ] = None

    database: Annotated[
        StatusInfo | None,
        Field(
            title="Database",
            description="Data about the database status.",
        ),
    ] = None

    memory_rss: Annotated[
        StatusInfo | None,
        Field(
            title="Memory RSS",
            description="Data about the memory RSS status.",
        ),
    ] = None

    redis: Annotated[
        StatusInfo | None,
        Field(
            title="Redis",
            description="Data about the Redis status.",
        ),
    ] = None


class HealthStatus(LockedModel):
    """Health status.

    Represents the runtime status of the iGEM Registry and its resources.

    Attributes:
        status (Literal): Overall health status of the Registry.
        info (ResourceData): Information about the Registry's resources.
        error (ResourceData): Errors encountered by the Registry's resources.
        details (ResourceData): Further details about the Registry's resources.

    """

    status: Annotated[
        Literal["ok", "error"],
        Field(
            title="Status",
            description="Registry health status.",
        ),
    ]

    info: Annotated[
        ResourceData,
        Field(
            title="Info",
            description="Information about the Registry's resources.",
        ),
    ]

    error: Annotated[
        ResourceData,
        Field(
            title="Error",
            description="Errors encountered by the Registry's resources.",
        ),
    ]

    details: Annotated[
        ResourceData,
        Field(
            title="Details",
            description="Further details about the Registry's resources.",
        ),
    ]


class Client:
    """Registry API client.

    Represents the main programmatic interface for interacting with iGEM
    Registry API managing connection, authentication, and user consent, with
    modes for offline, anonymous, and authenticated states.

    This class is **not** thread-safe and should not be shared across threads
    without external synchronization.
    """

    def __init__(
        self,
        base: str | None = "https://api.registry.igem.org/v1",
        *,
        verify: bool | str = True,
        timeout: None | float | tuple[float, None] | tuple[float, float] = (
            5.0,
            30.0,
        ),
        stream: bool = False,
        proxies: MutableMapping[str, str] | None = None,
        certificate: str | tuple[str, str] | None = None,
        redirects: bool = True,
        retries: NonNegativeInt = 3,
    ) -> None:
        """Registry API client.

        Represents the main programmatic interface for interacting with iGEM
        Registry API. It encapsulates connection management, authentication,
        and user consent handling.

        By default, the client starts in offline mode if `base` is not
        provided. With a valid base URL, `connect()` may be used to verify the
        Registry status and enter anonymous mode. For authenticated operations,
        `sign_in()` transitions the client into authenticated mode. Actions
        requiring user consent, such as part authoring or publishing, can be
        enabled via `opt_in()`.

        This class is **not** thread-safe. Do not share a single instance
        across threads without external synchronization.

        Args:
            base (str | None): Base URL of the Registry API. If provided, must
                be a valid HTTP URL. If `None`, the client is unable to connect
                to the Registry instance (offline mode).
            verify (bool | str): TLS verification setting passed to `requests`.
                Can be set to `False` (disables verification), `True` (enables
                verification), or a path to a CA bundle.
            timeout (None | float | tuple[float, None] | tuple[float, float]):
                Default timeout passed to `requests`. Either a `None` value to
                disable timeouts, a single float specifying both the connect
                and read timeouts, `(connect, None)` to disable read timeout,
                or `(connect, read)` enabling separate timeout values.
            stream (bool): Whether responses should be streamed by default.
            proxies (MutableMapping[str, str] | None): Proxy mapping passed to
                `requests`.
            certificate (str | tuple[str, str] | None): Path to the client
                certificate or a tuple of paths to the certificate and the
                corresponding key files.
            redirects (bool): Whether redirects are allowed by default.
            retries (NonNegativeInt): Retry budget for failed requests.

        Raises:
            InputValidationError: If the provided base URL is invalid.

        Examples:
           Create, connect, authenticate, and opt in with `Client`:

            ```python
            from igem_registry_api import Client

            client = Client()
            client.connect()
            client.sign_in("username", "password")
            client.opt_in()
            client.opt_out()
            client.sign_out()
            client.disconnect()
            ```

        """
        logger.info("Initializing client with base URL: %s", base)
        logger.debug(
            "Client configuration: %s",
            {
                "verify": verify,
                "timeout": timeout,
                "stream": stream,
                "proxies": proxies,
                "certificate": certificate,
                "redirects": redirects,
                "retries": retries,
            },
        )

        try:
            self.base: HttpUrl | None = (
                TypeAdapter(HttpUrl).validate_python(base.rstrip("/"))
                if base is not None
                else None
            )
        except ValidationError as e:
            raise InputValidationError(error=e) from e

        self.mode: Mode = Mode.NONE
        self.session: requests.Session = requests.Session()

        self.verify: bool | str = verify
        self.timeout: (
            None | float | tuple[float, None] | tuple[float, float]
        ) = timeout
        self.stream: bool = stream
        self.proxies: MutableMapping[str, str] | None = proxies
        self.certificate: str | tuple[str, str] | None = certificate
        self.redirects: bool = redirects
        self.retries: NonNegativeInt = retries

        self.ratelimit: RateLimit | None = None
        self.cooldown: NonNegativeInt = 0

        self.user: Account | None = None

    @classmethod
    def stub(cls) -> Self:
        """Create a stub client instance without initializing it.

        Returns:
            out (Client): A stub client instance.

        """
        inst = object.__new__(cls)

        inst.base = None
        inst.mode = Mode.NONE
        inst.user = None

        return inst

    @property
    def is_none(self) -> bool:
        """Check if the client is in offline mode."""
        return self.mode is Mode.NONE

    @property
    def is_anon(self) -> bool:
        """Check if the client is in anonymous mode."""
        return self.mode is Mode.ANON

    @property
    def is_auth(self) -> bool:
        """Check if the client is in authenticated mode."""
        return self.mode is Mode.AUTH

    @property
    def is_opted_in(self) -> bool:
        """Check if the client is opted in."""
        if self.user is None:
            return False
        return self.user.consent is True

    def connect(self) -> None:
        """Connect the client to the Registry.

        Raises:
            ClientConnectionError: If client connection fails.

        """
        logger.info("Connecting client to Registry at base URL: %s", self.base)
        if not self.is_none:
            raise ClientConnectionError(message="Client is already connected.")
        if self.base is None:
            raise ClientConnectionError(message="Base URL is not set.")

        self.mode = Mode.ANON

        try:
            health: HealthStatus = self.health()
        except Exception as e:
            self.mode = Mode.NONE
            raise ClientConnectionError(
                message="Failed to check health status.",
            ) from e

        if health.status != "ok":
            self.mode = Mode.NONE
            raise ClientConnectionError(
                message=f"Health check failed: '{health.status}'.",
            )

    @connected
    def disconnect(self) -> None:
        """Disconnect the client from the Registry.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Disconnecting client from Registry.")

        self.session.close()
        self.user = None
        self.mode = Mode.NONE

    @connected
    def health(self) -> HealthStatus:
        """Check the health of the Registry.

        Returns:
            out (HealthStatus): Runtime status of the Registry.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        return call(
            self,
            requests.Request(
                method="GET",
                url=f"{self.base}/health",
            ),
            HealthStatus,
        )

    @connected
    def sign_in(
        self,
        username: str,
        password: str,
        provider: str = "https://api.igem.org/v1",
    ) -> None:
        """Sign in to an account.

        Args:
            username (str): Username of the account.
            password (str): Password of the account.
            provider (str): Base URL of the identity provider granting
                authentication token.

        Raises:
            NotConnectedError: If the client is in offline mode.
            ClientAuthenticationError: If the authentication fails.

        """
        logger.info("Signing in to user account '%s'", username)

        if self.is_auth:
            raise ClientAuthenticationError(
                message="Client is already in authenticated mode.",
            )

        try:
            call(
                self,
                requests.Request(
                    method="POST",
                    url=f"{provider}/auth/sign-in",
                    headers={"Content-Type": "application/json"},
                    json={
                        "identifier": username,
                        "password": password,
                    },
                ),
            )
        except Exception as e:
            raise ClientAuthenticationError(
                message="Failed to authenticate account.",
            ) from e

        try:
            call(
                self,
                requests.Request(
                    method="GET",
                    url=f"{self.base}/auth/oauth/default/login",
                ),
            )
        except Exception as e:
            raise ClientAuthenticationError(
                message="Failed to generate authentication token.",
            ) from e

        self.mode = Mode.AUTH

        try:
            self.user = self.me()
        except Exception as e:
            self.mode = Mode.ANON
            raise ClientAuthenticationError(
                message="Failed to fetch authenticated account information.",
            ) from e

        self.user.username = username

    @authenticated
    def sign_out(self) -> None:
        """Sign out of the authenticated account.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        if self.user:
            logger.info("Signing out of account '%s'", self.user.username)

            call(
                self,
                requests.Request(
                    method="POST",
                    url=f"{self.base}/auth/sign-out",
                ),
            )

            self.session.cookies.clear()
            self.user = None
            self.mode = Mode.ANON

    @authenticated
    def me(self) -> Account:
        """Get information about the authenticated account.

        Returns:
            out (Account): Authenticated account.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        from .account import Account

        user = call(
            self,
            requests.Request(
                method="GET",
                url=f"{self.base}/auth/me",
            ),
            Account,
        )

        user.client = self

        return user

    @authenticated
    def opt_in(self) -> None:
        """Opt-in the authenticated account for authoring.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        if self.user:
            if self.user.consent:
                logger.info(
                    "User '%s' is already opted in",
                    self.user.username,
                )
                return

            logger.info("Opting in with account '%s'", self.user.username)

            call(
                self,
                requests.Request(
                    method="POST",
                    url=f"{self.base}/accounts/opt-in",
                ),
            )

            self.user.consent = True

    @authenticated
    def opt_out(self) -> None:
        """Opt-out the authenticated account from authoring.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        if self.user:
            if not self.user.consent:
                logger.info(
                    "User '%s' is not opted in",
                    self.user.username,
                )
                return

            logger.info("Opting out with account '%s'", self.user.username)

            call(
                self,
                requests.Request(
                    method="POST",
                    url=f"{self.base}/accounts/opt-out",
                ),
            )

            self.user.consent = False
