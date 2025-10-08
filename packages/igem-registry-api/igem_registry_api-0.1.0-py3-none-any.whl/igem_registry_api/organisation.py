"""Organisation models and operations.

This submodule defines classes related to Registry organisations. It provides
the `Organisation` model for representing and interacting with an organisation,
and the `Kind` enum for organisation types.

Exports:
    Organisation: Model representing a Registry organisation.
    Kind: Enum of organisation types.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

import requests
from pydantic import (
    UUID4,
    Field,
    HttpUrl,
    NonNegativeInt,
    SkipValidation,
    field_validator,
)

from igem_registry_api.errors import InputValidationError

from .calls import call, call_paginated
from .client import Client
from .schemas import AuditLog, CleanEnum, DynamicModel, Progress
from .utils import authenticated, connected

if TYPE_CHECKING:
    from typing import Literal, Self

    from .account import Account


logger: logging.Logger = logging.getLogger(__name__)


__all__: list[str] = [
    "Kind",
    "Organisation",
]


class Kind(CleanEnum):
    """Kinds of organisations.

    Defines the different types of organisations within the Registry API.

    Attributes:
        EDUCATION: Educational institutions.
        COMPANY: For-profit companies.
        NON_PROFIT: Non-profit organisations.
        GOVERNMENT: Government agencies.
        IGEM_TEAM: iGEM teams.
        OTHER: Other types of organisations.

    """

    EDUCATION = "education"
    COMPANY = "company"
    NON_PROFIT = "non-profit"
    GOVERNMENT = "government"
    IGEM_TEAM = "igem-team"
    OTHER = "other"


class Organisation(DynamicModel):
    """Registry organisation.

    Represents an organisation in the Registry. An `Organisation` stores basic
    information about the organisation, and when paired with an authenticated
    `Client`, can retrieve member accounts (`members()`). Organisations can
    also be retrieved with a connected `Client` in bulk via `fetch()` or
    individually using their UUID via `get()` methods.

    Attributes:
        client (Client): Registry API client used to perform requests.
        uuid (str | UUID4): Unique organisation identifier (version-4 UUID).
        name (str | None): Name of the organisation.
        kind (Kind | None): Kind of the organisation.
        link (HttpUrl | None): Website URL of the organisation.
        audit (AuditLog | None): Audit information for the organisation.

    Examples:
        Create an `Organisation` instance and fetch member `Accounts`:

        ```python
        from igem_registry_api import Client, Organisation

        client = Client()
        client.connect()
        client.sign_in("username", "password")

        org = Organisation(
            client=client,
            uuid="11111111-2222-3333-4444-555555555555",
        )

        accounts = org.members(order="desc")
        ```

        Retrieve organisations in bulk or individually:

        ```python
        from igem_registry_api import Client, Organisation

        client = Client()
        client.connect()
        client.sign_in("username", "password")

        organisations = Organisation.fetch(client, limit=5)
        print(Organisation.get(client, organisations[0].uuid))
        ```

    """

    client: Annotated[
        SkipValidation[Client],
        Field(
            title="Client",
            description="Registry API client.",
            frozen=False,
            exclude=True,
            repr=False,
        ),
    ] = Field(default_factory=Client.stub)

    uuid: Annotated[
        str | UUID4,
        Field(
            title="UUID",
            description="Unique identifier for the organisation.",
            frozen=True,
        ),
    ]

    name: Annotated[
        str | None,
        Field(
            title="Name",
            description="Name of the organisation.",
            frozen=True,
        ),
    ] = None

    kind: Annotated[
        Kind | None,
        Field(
            title="Kind",
            description="Kind of the organisation.",
            alias="type",
            frozen=True,
        ),
    ] = None

    link: Annotated[
        HttpUrl | None,
        Field(
            title="Link",
            description="Website URL of the organisation.",
            frozen=True,
        ),
    ] = None

    audit: Annotated[
        AuditLog | None,
        Field(
            title="Audit",
            description="Audit information for the organisation.",
            frozen=True,
            exclude=True,
            repr=False,
        ),
    ] = None

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4) -> UUID4:
        """Normalize the organisation UUID to a UUID4 instance.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4): Unique organisation identifier.

        Returns:
            out (UUID4): A validated version-4 UUID object.

        Raises:
            InputValidationError: If the input value is not a valid UUID4.

        """
        if isinstance(value, str):
            try:
                value = UUID(value, version=4)
            except Exception as e:
                raise InputValidationError(error=e) from e
        return value

    @authenticated
    def members(
        self,
        *,
        sort: Literal[
            "uuid",
            "firstName",
            "lastName",
            "systemRole",
            "photoURL",
        ] = "firstName",
        order: Literal["asc", "desc"] = "asc",
        limit: NonNegativeInt | None = None,
        progress: Progress | None = None,
    ) -> list[Account]:
        """List member accounts of the organisation.

        Args:
            sort (Literal): Field to sort the member accounts by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of member accounts to
                retrieve. If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Account]): Member accounts belonging to the organisation.
                Only opted-in user accounts are included in the response.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        from .account import Account

        logger.info(
            "Fetching member accounts for the organisation: %s",
            self.uuid,
        )

        items, _ = call_paginated(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/organisations/{self.uuid}/members",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            Account,
            limit=limit,
            progress=progress,
        )

        logger.info(
            "Fetched %d member accounts for the organisation: %s",
            len(items),
            self.uuid,
        )

        for item in items:
            item.client = self.client
            item.consent = True

        return items

    @classmethod
    @connected
    def fetch(
        cls,
        client: Client,
        *,
        sort: Literal[
            "uuid",
            "name",
            "type",
            "link",
            "audit.created",
            "audit.updated",
        ] = "name",
        order: Literal["asc", "desc"] = "asc",
        limit: NonNegativeInt | None = None,
        progress: Progress | None = None,
    ) -> list[Self]:
        """List organisations in the Registry.

        Args:
            client (Client): Registry API client used to perform requests.
            sort (Literal): Field to sort the organisations by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of organisations to
                retrieve. If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Organisation]): Organisations.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Fetching organisations.")

        items, _ = call_paginated(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/organisations",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            cls,
            limit=limit,
            progress=progress,
        )

        logger.info("Fetched %d organisations.", len(items))

        for item in items:
            item.client = client

        return items

    @classmethod
    @connected
    def get(cls, client: Client, uuid: str | UUID4) -> Self:
        """Retrieve an organisation by its UUID.

        Args:
            client (Client): Registry API client used to perform requests.
            uuid (str | UUID4): Unique organisation identifier.

        Returns:
            out (Organisation): Requested organisation.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Retrieving organisation: %s.", uuid)

        item = call(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/organisations/{uuid}",
            ),
            cls,
        )

        logger.info("Retrieved organisation: %s.", uuid)

        item.client = client

        return item
