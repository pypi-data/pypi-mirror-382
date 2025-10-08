"""License models and lookups.

This submodule defines the `License` model used for licensing of Registry
parts. All defined licenses are available for fast local lookup as class
constants.

Exports:
    License: Model representing a license.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, ClassVar
from uuid import UUID

import requests
from pydantic import (
    UUID4,
    Field,
    HttpUrl,
    NonNegativeInt,
    TypeAdapter,
    field_validator,
)

from .calls import call, call_paginated
from .errors import InputValidationError, NotFoundError
from .schemas import LockedModel, Progress
from .utils import connected

if TYPE_CHECKING:
    from typing import Literal, Self

    from .client import Client


logger: logging.Logger = logging.getLogger(__name__)


__all__: list[str] = [
    "License",
]


class License(LockedModel):
    """Content license.

    Represents a license used to define the use, copy, and distribution of
    Registry parts. Available licenses are defined as class constants (e.g.
    `License.MIT`) and stored in an in-memory catalog for direct use in code.

    Licenses can be resolved locally via `from_uuid()` or `from_id()`, or
    retrieved remotely through the API using `fetch()` and `get()`.

    Attributes:
        uuid (str | UUID4): Unique identifier for the license
            (version-4 UUID).
        spdx_id (str | None): SPDX identifier for the license.
        name (str | None): Name of the license.
        description (str | None): Brief description of the license.
        icon (HttpUrl | None): URL to the license icon.
        source (HttpUrl | None): URL to the license source.
        approved (bool | None): Whether the license is OSI approved.

    Examples:
        Access a predefined license:

        ```python
        from igem_registry_api import License

        lic = License.MIT
        print(lic.uuid, lic.spdx_id, lic.name)
        ```

        Resolve licenses from the in-memory catalog:
        ```python
        from igem_registry_api import License

        lic1 = License.from_id("mit")
        lic2 = License.from_uuid("6aeb281a-d268-44da-8bdc-a80e2dce5692")

        print(lic1 is lic2)
        ```

        Retrieve licenses from the Registry API:
        ```python
        from igem_registry_api import Client, License

        client = Client()
        client.connect()

        licenses = License.fetch(client, limit=5)
        print(License.get(client, licenses[0].uuid))
        ```

    """

    uuid: Annotated[
        str | UUID4,
        Field(
            title="UUID",
            description="Unique identifier for the license.",
        ),
    ]

    spdx_id: Annotated[
        str | None,
        Field(
            title="SPDX ID",
            description="SPDX identifier for the license.",
            alias="spdxID",
        ),
    ] = None

    name: Annotated[
        str | None,
        Field(
            title="Name",
            description="Name of the license.",
            alias="title",
        ),
    ] = None

    description: Annotated[
        str | None,
        Field(
            title="Description",
            description="Brief description of the license.",
        ),
    ] = None

    icon: Annotated[
        HttpUrl | None,
        Field(
            title="Icon",
            description="URL to the license icon.",
        ),
    ] = None

    source: Annotated[
        HttpUrl | None,
        Field(
            title="Source",
            description="URL to the license source.",
            alias="url",
        ),
    ] = None

    approved: Annotated[
        bool | None,
        Field(
            title="OSI Approved",
            description="Whether the license is OSI approved.",
            alias="osiApproved",
        ),
    ] = None

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4) -> UUID4:
        """Normalize the license UUID to a UUID4 instance.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4): Unique license identifier.

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

    @classmethod
    def from_uuid(cls, uuid: str | UUID4) -> Self:
        """Resolve a license from its UUID.

        Accepts both `str` and `UUID4` objects for usability, normalizes to a
        v4 UUID string, and looks it up from the in-memory catalog.

        Args:
            uuid (str | UUID4): Unique license identifier.

        Returns:
            out (License): Matching license.

        Raises:
            NotFoundError: If no license exists for the given UUID.

        """
        key = str(UUID(uuid, version=4) if isinstance(uuid, str) else uuid)
        logger.debug("Resolving license by uuid: %s.", key)
        try:
            return cls.CATALOG[key]
        except KeyError as e:
            raise NotFoundError(item="license", key="uuid", value=key) from e

    @classmethod
    def from_id(cls, identifier: str) -> Self:
        """Resolve a license from its SPDX ID.

        Args:
            identifier (str): License SPDX ID.

        Returns:
            out (License): Matching license.

        Raises:
            NotFoundError: If no license exists for the given SPDX ID.

        """
        key = identifier
        logger.debug("Resolving license by SPDX ID: %s.", key)
        try:
            return cls.CATALOG[key]
        except KeyError as e:
            raise NotFoundError(
                item="license",
                key="SPDX ID",
                value=key,
            ) from e

    @classmethod
    @connected
    def fetch(
        cls,
        client: Client,
        *,
        sort: Literal[
            "uuid",
            "spdxID",
            "title",
            "description",
            "icon",
            "url",
            "osiApproved",
        ] = "title",
        order: Literal["asc", "desc"] = "asc",
        limit: NonNegativeInt | None = None,
        progress: Progress | None = None,
    ) -> list[Self]:
        """List licenses from the Registry.

        Args:
            client (Client): Registry API client used to perform requests.
            sort (Literal): Field to sort the licenses by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of licenses to
                retrieve. If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[License]): Part licenses.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Fetching licenses.")

        items, _ = call_paginated(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/licenses",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            cls,
            limit=limit,
            progress=progress,
        )

        logger.info("Fetched %d licenses.", len(items))

        return items

    @classmethod
    @connected
    def get(cls, client: Client, uuid: str | UUID4) -> Self:
        """Retrieve a license by its UUID.

        Args:
            client (Client): Registry API client used to perform requests.
            uuid (str | UUID4): Unique license identifier.

        Returns:
            out (License): Requested license.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Retrieving license: %s.", uuid)

        item = call(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/licenses/{uuid}",
            ),
            cls,
        )

        logger.info("Retrieved license: %s.", uuid)

        return item

    CATALOG: ClassVar[dict[str, Self]]

    APACHE: ClassVar[Self]
    CC_BY: ClassVar[Self]
    CC_BY_SA: ClassVar[Self]
    CC0: ClassVar[Self]
    GPL: ClassVar[Self]
    MIT: ClassVar[Self]


License.APACHE = License(
    uuid=UUID("bc058bb8-abd9-419a-860e-43b0889cad89"),
    spdx_id="apache-2.0",
    name="Apache License 2.0",
    source=TypeAdapter(HttpUrl).validate_python(
        "http://www.apache.org/licenses/LICENSE-2.0",
    ),
    description=(
        "A permissive license whose main conditions require preservation of "
        "copyright and license notices. Contributors provide an express grant "
        "of patent rights. Licensed works, modifications, and larger works "
        "may be distributed under different terms and without source code."
    ),
    approved=True,
)
License.CC_BY = License(
    uuid=UUID("d6c69ca7-8be4-4bc0-b4a8-d3ae1d428aa6"),
    spdx_id="cc-by-4.0",
    name="Creative Commons Attribution 4.0 International",
    description=(
        "The Creative Commons Attribution license allows re-distribution "
        "and re-use of a licensed work on the condition that the creator "
        "is appropriately credited."
    ),
    source=TypeAdapter(HttpUrl).validate_python(
        "https://creativecommons.org/licenses/by/4.0/legalcode",
    ),
    approved=False,
)
License.CC_BY_SA = License(
    uuid=UUID("4e38c689-4c47-456a-9e78-e11caddaa983"),
    spdx_id="cc-by-sa-4.0",
    name="Creative Commons Attribution Share Alike 4.0 International",
    description=(
        "Permits almost any use subject to providing credit and license "
        "notice. Frequently used for media assets and educational "
        "materials. The most common license for Open Access scientific "
        "publications."
    ),
    source=TypeAdapter(HttpUrl).validate_python(
        "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
    ),
    approved=False,
)
License.CC0 = License(
    uuid=UUID("5b2a6fd4-f5fa-4626-a37f-35f1ea89eec7"),
    spdx_id="cc0-1.0",
    name="Creative Commons Zero v1.0 Universal",
    description=(
        "CC0 waives copyright interest in a work you've created and "
        "dedicates it to the world-wide public domain. Use CC0 to opt out "
        "of copyright entirely and ensure your work has the widest reach."
    ),
    source=TypeAdapter(HttpUrl).validate_python(
        "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
    ),
    approved=False,
)
License.GPL = License(
    uuid=UUID("403dfaa8-883c-4e91-892f-ddd2f927f670"),
    spdx_id="gpl-3.0-or-later",
    name="GNU General Public License v3.0 or later",
    description=(
        "Permissions of this strong copyleft license are conditioned on "
        "making available complete source code of licensed works and "
        "modifications, which include larger works using a licensed work, "
        "under the same license. Copyright and license notices must be "
        "preserved. Contributors provide an express grant of patent "
        "rights."
    ),
    source=TypeAdapter(HttpUrl).validate_python(
        "https://www.gnu.org/licenses/gpl-3.0-standalone.html",
    ),
    approved=True,
)
License.MIT = License(
    uuid=UUID("6aeb281a-d268-44da-8bdc-a80e2dce5692"),
    spdx_id="mit",
    name="MIT License",
    description=(
        "A short and simple permissive license with conditions only "
        "requiring preservation of copyright and license notices. "
        "Licensed works, modifications, and larger works may be "
        "distributed under different terms and without source code."
    ),
    source=TypeAdapter(HttpUrl).validate_python(
        "https://opensource.org/licenses/MIT",
    ),
    approved=True,
)

License.CATALOG = {
    str(key): value
    for value in [
        License.APACHE,
        License.CC_BY,
        License.CC_BY_SA,
        License.CC0,
        License.GPL,
        License.MIT,
    ]
    for key in (value.uuid, value.spdx_id)
}
