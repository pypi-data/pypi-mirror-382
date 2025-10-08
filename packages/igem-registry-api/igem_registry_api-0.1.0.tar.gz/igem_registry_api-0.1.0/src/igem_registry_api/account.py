"""Account models and operations.

This submodule defines classes related to Registry user accounts. It provides
the `Account` model for representing and interacting with a Registry account,
and the `Roles` enum for account system roles.

Exports:
    Account: Model representing a Registry account.
    Roles: Enum of system roles.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

import requests
from pydantic import (
    UUID4,
    Field,
    NonNegativeInt,
    SkipValidation,
    field_validator,
)

from .calls import call_paginated
from .client import Client
from .errors import InputValidationError
from .schemas import CleanEnum, DynamicModel, Progress
from .utils import authenticated

if TYPE_CHECKING:
    from typing import Literal

    from .organisation import Organisation
    from .part import Part


logger: logging.Logger = logging.getLogger(__name__)


__all__: list[str] = [
    "Account",
    "Roles",
]


class Roles(CleanEnum):
    """System roles of Registry accounts.

    Defines the access level within the Registry API.

    Attributes:
        ADMIN: Privileged users with full access.
        USER: Standard accounts with limited access.

    """

    ADMIN = "admin"
    USER = "user"


class Account(DynamicModel):
    """Registry account.

    Represents a user account in the Registry. An `Account` stores basic
    profile information and, when paired with an authenticated `Client`, can
    retrieve affiliated organisations (`affiliations()`) and authored parts
    (`parts()`).


    Attributes:
        client (Client): Registry API client used to perform requests.
        uuid (str | UUID4): Unique account identifier (version-4 UUID).
        username (str | None): Username of the account.
        role (Roles | None): System role of the account.
        first_name (str | None): Given name of the account user.
        last_name (str | None): Family name of the account user.
        photo (str | None): Photo URL associated with the account.
        consent (bool | None): Whether the account user has opted in as a
            Registry author.

    Examples:
        Create an `Account` instance and fetch affiliated `Organisations` and
        authored `Parts`:

        ```pythonuuid
        from igem_registry_api import Account, Client

        client = Client()
        client.connect()
        client.sign_in("username", "password")

        account = Account(
            client=client,
            uuid="11111111-2222-3333-4444-555555555555",
        )

        orgs = account.affiliations(order="desc")
        parts = account.parts(limit=200)
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
            description="Unique identifier for the account.",
            frozen=True,
        ),
    ]

    username: Annotated[
        str | None,
        SkipValidation,
        Field(
            title="Username",
            description="Username of the account.",
            frozen=False,
            exclude=True,
            repr=False,
        ),
    ] = None

    role: Annotated[
        Roles | None,
        Field(
            title="Role",
            description="System role of the account.",
            alias="systemRole",
            frozen=True,
        ),
    ] = None

    first_name: Annotated[
        str | None,
        Field(
            title="First Name",
            description="Given name of the account user.",
            alias="firstName",
            frozen=True,
        ),
    ] = None

    last_name: Annotated[
        str | None,
        Field(
            title="Last Name",
            description="Family name of the account user.",
            alias="lastName",
            frozen=True,
        ),
    ] = None

    photo: Annotated[
        str | None,
        Field(
            title="Photo",
            description="Photo URL associated with the account.",
            alias="photoURL",
            frozen=True,
        ),
    ] = None

    consent: Annotated[
        bool | None,
        Field(
            title="Consent",
            description=(
                "Whether the account user has opted in as a Registry author."
            ),
            alias="optedIn",
            frozen=False,
        ),
    ] = None

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4) -> UUID4:
        """Normalize the account UUID to a UUID4 instance.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4): Unique account identifier.

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
    def affiliations(
        self,
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
    ) -> list[Organisation]:
        """List account affiliations.

        Args:
            sort (Literal): Field to sort the organisations by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of organisations to
                retrieve. If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Organisation]): Organisations the account belongs to.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        from .organisation import Organisation

        logger.info(
            "Fetching affiliated organisations for the account: %s",
            self.uuid,
        )

        items, _ = call_paginated(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/accounts/{self.uuid}/affiliations",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            Organisation,
            limit=limit,
            progress=progress,
        )

        logger.info(
            "Fetched %d affiliated organisations for the account: %s",
            len(items),
            self.uuid,
        )

        for item in items:
            item.client = self.client

        return items

    @authenticated
    def parts(
        self,
        *,
        sort: Literal[
            "uuid",
            "name",
            "slug",
            "status",
            "title",
            "description",
            "type.uuid",
            "type.label",
            "type.slug",
            "licenseUUID",
            "source",
            "sequence",
            "audit.created",
            "audit.updated",
        ] = "audit.created",
        order: Literal["asc", "desc"] = "asc",
        limit: NonNegativeInt | None = None,
        progress: Progress | None = None,
    ) -> list[Part]:
        """List parts authored by the account user.

        Args:
            sort (Literal): Field to sort the parts by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of parts to retrieve.
                If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Part]): Parts authored by the account user.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        from .part import Part

        logger.info(
            "Fetching authored parts for the account: %s",
            self.uuid,
        )

        items, _ = call_paginated(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/parts/accounts/{self.uuid}",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            Part,
            limit=limit,
            progress=progress,
        )

        logger.info(
            "Fetched %d authored parts for the account: %s",
            len(items),
            self.uuid,
        )

        for item in items:
            item.client = self.client

        return items
