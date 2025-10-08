"""Author models and contribution roles.

This submodule defines models related to authorship in the Registry. It
provides the `Author` model, which combines `Account` and `Organisation`
information with contribution roles defined by the `Contribution` enum.

Exports:
    Author: Model representing a Registry author.
    Contribution: Enum of author contribution roles.
"""

from collections.abc import Iterable
from typing import Annotated
from uuid import UUID

from pydantic import (
    UUID4,
    Field,
    field_validator,
    model_validator,
)

from igem_registry_api.errors import InputValidationError

from .account import Account
from .organisation import Organisation
from .schemas import CleanEnum, DynamicModel

__all__: list[str] = [
    "Author",
    "Contribution",
]


class Contribution(CleanEnum):
    """Contribution roles of Registry authors.

    Defines the contributor roles supported by the Registry, adapted from the
    CRediT taxonomy. Multiple authors can share the same role, and one author
    can hold several roles.

    Attributes:
        CONCEPTUALISATION: Formulating research goals or overarching ideas.
        DATA_CURATION: Managing, annotating, and maintaining research data.
        FORMAL_ANALYSIS: Applying formal techniques to analyse study data.
        INVESTIGATION: Performing experiments or collecting evidence.
        METHODOLOGY: Designing methods or creating models.
        SUPERVISION: Providing oversight, leadership, or mentorship.
        VALIDATION: Verifying results and reproducibility of outputs.
        VISUALISATION: Preparing or presenting visual representations.
        WRITING: Drafting and authoring written outputs.

    """

    CONCEPTUALISATION = "conceptualisation"
    DATA_CURATION = "data-curation"
    FORMAL_ANALYSIS = "formal-analysis"
    INVESTIGATION = "investigation"
    METHODOLOGY = "methodology"
    SUPERVISION = "supervision"
    VALIDATION = "validation"
    VISUALISATION = "visualisation"
    WRITING = "writing"


class Author(DynamicModel):
    """Registry author.

    Represents an author entry in the Registry, combining the underlying
    `Account`, associated `Organisation`, and the author's specific
    `Contribution` roles.

    Attributes:
        uuid (str | UUID4 | None): Unique author identifier (version-4 UUID).
        organisation (Organisation): Organisation the author is affiliated
            with.
        account (Account): User account of the author.
        contributions (Iterable[Contribution]): Contribution roles of the
            author.

    Examples:
        Create an `Author` instance:

        ```python
        from igem_registry_api import (
            Account,
            Author,
            Contribution,
            Organisation,
        )

        author = Author(
            account=Account(
                uuid="11111111-2222-3333-4444-555555555555",
            ),
            organisation=Organisation(
                uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            ),
            contributions=[
                Contribution.INVESTIGATION,
                Contribution.WRITING,
            ],
        )
        ```

    """

    uuid: Annotated[
        str | UUID4 | None,
        Field(
            title="UUID",
            description="Unique identifier for the author.",
            frozen=True,
        ),
    ] = None

    organisation: Annotated[
        Organisation,
        Field(
            title="Organisation",
            description="Organisation the author belongs to.",
            alias="organisationUUID",
            frozen=False,
        ),
    ]

    account: Annotated[
        Account,
        Field(
            title="Account",
            description="Account of the author.",
            alias="accountUUID",
            frozen=False,
        ),
    ]

    contributions: Annotated[
        Iterable[Contribution],
        Field(
            title="Contributions",
            description="Contributions of the author.",
            alias="roles",
            frozen=False,
        ),
    ]

    @model_validator(mode="before")
    @classmethod
    def extract_account(cls, data: dict) -> dict:
        """Extract nested account data from raw API response.

        Converts `accountUUID`, `firstName`, and `lastName` fields from the raw
        API response into an embedded `Account` object structure.

        Args:
            data (dict): Raw data response from the API.

        Returns:
            out (dict): Normalized data with an `Account` sub-object.

        """
        if "accountUUID" in data:
            data["account"] = {
                "uuid": data.pop("accountUUID"),
                "first_name": data.pop("firstName"),
                "last_name": data.pop("lastName"),
                "consent": True,  # Only opted-in users can be authors
            }
        return data

    @model_validator(mode="before")
    @classmethod
    def extract_organisation(cls, data: dict) -> dict:
        """Extract nested organisation data from raw API response.

        Converts the `organisationUUID` field from the raw API response into
        an embedded `Organisation` object structure.

        Args:
            data (dict): Raw data response from the API.

        Returns:
            out (dict): Normalized data with an `Organisation` sub-object.

        """
        if "organisationUUID" in data:
            data["organisation"] = {"uuid": data.pop("organisationUUID")}
        return data

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4 | None) -> UUID4 | None:
        """Normalize the author UUID to a UUID4 instance, if provided.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4 | None): Unique author identifier.

        Returns:
            out (UUID4 | None): A validated version-4 UUID object or `None`.

        Raises:
            InputValidationError: If the input value is not a valid UUID4.

        """
        if isinstance(value, str):
            try:
                value = UUID(value, version=4)
            except Exception as e:
                raise InputValidationError(error=e) from e
        return value

    @field_validator("contributions", mode="after")
    @classmethod
    def ensure_set(cls, value: Iterable[Contribution]) -> set[Contribution]:
        """Normalize contributions to a set of unique contribution roles.

        Accepts any iterable (e.g., `list`, `tuple`, `set`) for usability,
        while ensuring the stored value is always a `set`. This avoids
        type-checker complaints for a non-`set` input, while also removing
        duplicates and ignoring order.

        Args:
            value (Iterable[Contribution]): Author contributions.

        Returns:
            out (set[Contribution]): Unique contributions as a set.

        Raises:
            InputValidationError: If the input value is not a valid UUID4.

        """
        try:
            value = set(value)
        except Exception as e:
            raise InputValidationError(error=e) from e
        return value
