"""Part models and operations.

This submodule defines classes related to Registry parts. It provides
the `Part` model for representing and interacting with a part, `Reference`
model for referencing parts by UUID or slug, and the `Compatibility` model for
checking assembly compatibility, as well as the `Status` enum for part statuses
and the `Standard` enum listing assembly standards supported by the Registry.

Exports:
    Part: Model representing a Registry part.
    Reference: Model representing a reference to a part.
    Compatibility: Model representing assembly compatibility.
    Status: Enum of part statuses.
    Standard: Enum of assembly standards.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING, Annotated, ClassVar, Literal
from uuid import UUID

import requests
from Bio.Seq import Seq
from pydantic import (
    UUID4,
    Field,
    NonNegativeInt,
    RootModel,
    SkipValidation,
    field_serializer,
    field_validator,
    model_validator,
)

from .annotation import Annotation
from .author import Author
from .calls import call, call_paginated
from .category import Category
from .client import Client
from .errors import InputValidationError
from .license import License
from .organisation import Organisation
from .schemas import AuditLog, CleanEnum, DynamicModel, LockedModel
from .type import Type
from .utils import connected

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Self

logger = logging.getLogger(__name__)


__all__: list[str] = [
    "Compatibility",
    "Part",
    "Reference",
    "Standard",
    "Status",
]


class Status(CleanEnum):
    """Part status.

    Defines the lifecycle stages of a Registry part.

    Attributes:
        DRAFT: Part is a draft and not yet submitted for review.
        SCREENING: Part is under review.
        PUBLISHED: Part has been reviewed and published.
        REJECTED: Part has been reviewed and rejected.

    """

    DRAFT = "draft"
    SCREENING = "screening"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Standard(CleanEnum):
    """Part standard.

    Defines the assembly standards supported by the Registry.

    Attributes:
        RFC10: "BioBrick" assembly standard (doi: 1721.1/45138).
        RFC12: "BioBrick 2" assembly standard (doi: 1721.1/45139).
        RFC21: "BglBrick" assembly standard (doi: 1721.1/46747).
        RFC23: "Silver" assembly standard (doi: 1721.1/32535).
        RFC25: "Freiburg" assembly standard (doi: 1721.1/45140).
        RFC1000: "TypeIIS" assembly standard.

    """

    RFC10 = "rfc10"
    RFC12 = "rfc12"
    RFC21 = "rfc21"
    RFC23 = "rfc23"
    RFC25 = "rfc25"
    RFC1000 = "rfc1000"


class Compatibility(LockedModel):
    """Part compatibility.

    Represents a compatibility between two assembly standards.

    Attributes:
        with_standard (Standard): The compatible assembly standard.
        overhang (str): The overhang sequence used for compatibility.

    """

    compatible: Annotated[
        bool,
        Field(
            title="Compatible",
            description="Whether the part is compatible with the standard.",
        ),
    ]
    motif: Annotated[
        Seq | None,
        Field(
            title="Motif",
            description="Forbidden motif sequence found.",
        ),
    ] = None
    position: Annotated[
        int | None,
        Field(
            title="Position",
            description=(
                "Position of the found forbidden motif in the part sequence."
            ),
            alias="index",
        ),
    ] = None

    motifs: ClassVar[dict[Standard, list[Seq]]] = {
        Standard.RFC10: [
            Seq("GAATTC"),  # EcoRI
            Seq("TCTAGA"),  # XbaI
            Seq("ACTAGT"),  # SpeI
            Seq("CTGCAG"),  # PstI
            Seq("GCGGCCGC"),  # NotI
        ],
        Standard.RFC12: [
            Seq("GAATTC"),  # EcoRI
            Seq("TCTAGA"),  # XbaI
            Seq("ACTAGT"),  # SpeI
            Seq("CTGCAG"),  # PstI
            Seq("GCGGCCGC"),  # NotI
            Seq("GCTAGC"),  # NheI
            Seq("GCCGGC"),  # NgoMIV
            Seq("ACCGGT"),  # AgeI
        ],
        Standard.RFC21: [
            Seq("GAATTC"),  # EcoRI
            Seq("AGATCT"),  # BglII
            Seq("GGATCC"),  # BamHI
            Seq("CTCGAG"),  # XhoI
        ],
        Standard.RFC23: [
            Seq("GAATTC"),  # EcoRI
            Seq("TCTAGA"),  # XbaI
            Seq("ACTAGT"),  # SpeI
            Seq("CTGCAG"),  # PstI
        ],
        Standard.RFC25: [
            Seq("GAATTC"),  # EcoRI
            Seq("TCTAGA"),  # XbaI
            Seq("ACTAGT"),  # SpeI
            Seq("CTGCAG"),  # PstI
            Seq("GCCGGC"),  # NgoMIV
            Seq("ACCGGT"),  # AgeI
        ],
        Standard.RFC1000: [
            Seq("GGTCTC"),  # BsaI
            Seq("GAGACC"),  # BsaI (reverse complement)
            Seq("GCTCTTC"),  # SapI
            Seq("GAAGAGC"),  # SapI (reverse complement)
        ],
    }

    @classmethod
    def check(cls, sequence: Seq, standard: Standard) -> Self:
        """Check compatibility of a sequence with a given standard.

        Args:
            sequence (Seq): The sequence to check.
            standard (Standard): The assembly standard to check against.

        Returns:
            out (Compatibility): The compatibility result.

        """
        logger.debug("Checking compatibility with standard '%s'.", standard)

        if standard not in cls.motifs:
            msg = f"Unsupported assembly standard '{standard}'."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e

        for motif in cls.motifs.get(standard, []):
            if motif in sequence:
                return cls(
                    compatible=False,
                    motif=motif,
                    position=sequence.index(motif),
                )

        return cls(compatible=True)


class Reference(DynamicModel):
    """Reference to a Registry part.

    Represents a reference to a part, identified by either its UUID or slug.
    At least one identifier must be provided. Can be used to fetch the full
    part details from the Registry using the `Part.get` method.

    Attributes:
        uuid (str | UUID4 | None): Unique identifier for the part.
        slug (str | None): URL-friendly identifier for the part.

    Examples:
        Creating references by UUID or slug, and fetching the corresponding
        part:

        ```python
        from igem_registry_api import Client, Part, Reference

        ref_by_uuid = Reference(uuid="123e4567-e89b-12d3-a456-426614174000")
        ref_by_slug = Reference(slug="bba-0000000001")

        Part.get(client, ref_by_uuid)
        Part.get(client, ref_by_slug)
        ```

    """

    uuid: Annotated[
        str | UUID4 | None,
        Field(
            title="UUID",
            description="Unique identifier for the part.",
            frozen=True,
        ),
    ] = None

    slug: Annotated[
        str | None,
        Field(
            title="Slug",
            description="The URL-friendly identifier for the part.",
            pattern=r"^bba-[a-z0-9]{1,10}$",
            frozen=True,
        ),
    ] = None

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4) -> UUID4:
        """Normalize the part UUID to a UUID4 instance.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4): Unique part identifier.

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

    @model_validator(mode="after")
    def check_input_provided(self) -> Self:
        """Ensure that at least one identifier is provided.

        Raises:
            InputValidationError: If neither `slug` nor `uuid` is provided.

        """
        if not self.slug and not self.uuid:
            msg = "Either slug or uuid must be provided."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e
        return self


class Part(DynamicModel):
    """Registry part.

    Represents a biological part in the Registry. A `Part` stores detailed
    information about the part, including its sequence and metadata. When
    paired with a connected `Client`, it can be used to load related data such
    as its composition (`load_composition`), sequence annotations
    (`load_annotations`), and authorship information (`load_authors`), as well
    as its usage in other parts (`uses`) and identical parts (`twins`).

    Parts can also be retrieved in bulk via the `fetch()` or `search()`
    methods, with the latter allowing for a query string to be specified.
    Individual parts can be retrieved using their UUID or slug via the `get()`
    method with the help of a `Reference` object.

    Attributes:
        client (Client): Registry API client used to perform requests.
        uuid (str | UUID4 | None): Unique identifier for the part (version-4
            UUID).
        id (str | None): The internal identifier for the part.
        slug (str | None): The URL-friendly identifier for the part.
        name (str | None): The name of the part.
        status (Status | None): The current status of the part.
        title (str | None): The title of the part.
        source (str | None): The source of the part.
        description (str | None): A brief description of the part.
        type (Type | None): The type of the part.
        categories (list[Category] | None): The categories associated with the
            part.
        license (License | None): The license under which the part is released.
        sequence (Seq | None): The sequence of the part.
        deleted (datetime | None): The deletion timestamp of the part, if
            applicable.
        audit (AuditLog | None): Audit information for the part.
        composition (list[Reference | Seq] | Seq | None): Composition of the
            part, which can be a list of references or a raw sequence.
        authors (list[Author] | None): The authors of the part.
        annotations (list[Annotation] | None): The sequence annotations of the
            part.

    Examples:
        Create a `Part` instance and fetch its composition, annotations, and
        authors:

        ```python
        from igem_registry_api import Client, Part, Reference

        client = Client()
        client.connect()

        part = Part.get(
            client=client,
            Reference(
                uuid="123e4567-e89b-12d3-a456-426614174000",
            ),
        )

        part.load_composition()
        part.load_annotations()
        part.load_authors()
        ```

        Retrieve parts in bulk or individually:

        ```python
        from igem_registry_api import Client, Part, Reference

        client = Client()
        client.connect()

        parts = Part.fetch(client, limit=5)
        print(Part.get(client, Reference(uuid=parts[0].uuid)))
        print(Part.get(client, Reference(slug=parts[0].slug)))
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
        str | UUID4 | None,
        Field(
            title="UUID",
            description="Unique identifier for the part.",
            frozen=True,
        ),
    ] = None
    id: Annotated[
        str | None,
        Field(
            title="ID",
            description="The identifier for the part.",
            frozen=True,
            exclude=True,
            repr=False,
        ),
    ] = None
    slug: Annotated[
        str | None,
        Field(
            title="Slug",
            description="The URL-friendly identifier for the part.",
            pattern=r"^bba-[a-z0-9]{1,10}$",
            frozen=True,
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            title="Name",
            description="The name of the part.",
            pattern=r"^BBa_[A-Z0-9]{1,10}$",
            frozen=True,
            repr=False,
        ),
    ] = None
    status: Annotated[
        Status | None,
        Field(
            title="Status",
            description="The current status of the part.",
            frozen=True,
        ),
    ] = None

    title: Annotated[
        str | None,
        Field(
            title="Title",
            description="The title of the part.",
            # min_length=3,
            # max_length=100,
            frozen=False,
        ),
    ] = None
    source: Annotated[
        str | None,
        Field(
            title="Source",
            description="The source of the part.",
            # max_length=250,
            frozen=False,
        ),
    ] = None
    description: Annotated[
        str | None,
        Field(
            title="Description",
            description="A brief description of the part.",
            frozen=False,
        ),
    ] = None
    type: Annotated[
        Type | None,
        Field(
            title="Type",
            description="The type of the part.",
            alias="typeUUID",
            frozen=False,
        ),
    ] = None
    categories: Annotated[
        Sequence[Category] | None,
        Field(
            title="Categories",
            description="The categories associated with the part.",
            frozen=False,
            exclude=True,
            repr=False,
        ),
    ] = Field(default_factory=list)
    license: Annotated[
        License | None,
        Field(
            title="License",
            description="The license under which the part is released.",
            alias="licenseUUID",
            frozen=False,
        ),
    ] = None
    sequence: Annotated[
        Seq | None,
        Field(
            title="Sequence",
            description="The sequence of the part.",
            frozen=True,
        ),
    ] = None
    deleted: Annotated[
        datetime | None,
        Field(
            title="Deleted",
            description="The deletion timestamp of the part, if applicable.",
            alias="deletedAt",
            frozen=True,
            exclude=True,
            repr=False,
        ),
    ] = None
    audit: Annotated[
        AuditLog | None,
        Field(
            title="Audit",
            description="Audit information for the part.",
            frozen=True,
            exclude=True,
            repr=False,
        ),
    ] = None

    composition: Annotated[
        Sequence[Reference | Seq] | Seq | None,
        Field(
            title="Composition",
            description=(
                "Composition of the part, which can be a list of references "
                "or a raw sequence."
            ),
            frozen=False,
        ),
    ] = None
    authors: Annotated[
        Sequence[Author] | None,
        Field(
            title="Authors",
            description="The authors of the part.",
            frozen=False,
        ),
    ] = Field(default_factory=list)
    annotations: Annotated[
        Sequence[Annotation] | None,
        Field(
            title="Annotations",
            description="The sequence annotations of the part.",
            frozen=False,
        ),
    ] = Field(default_factory=list)

    @property
    def is_composite(self) -> bool:
        """Check if the part is composite.

        A part is considered composite if its composition is defined and
        contains at least one `Reference` object.

        Returns:
            out (bool): `True` if the part is composite, `False` otherwise.

        """
        if isinstance(self.composition, Sequence):
            return any(isinstance(x, Reference) for x in self.composition)
        return False

    @property
    def compatibilities(self) -> dict[Standard, Compatibility]:
        """Report compatibility of the part with assembly standards.

        Verifies the part's sequence against forbidden motifs for RFC10 and
        RFC1000 assembly standards.

        Returns:
            out (dict[Standard, Compatibility]): Compatibility results.

        Raises:
            InputValidationError: If the part sequence is not available.

        """
        if not self.sequence:
            msg = "Part sequence is not available."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e

        return {
            Standard.RFC10: Compatibility.check(
                self.sequence,
                Standard.RFC10,
            ),
            Standard.RFC1000: Compatibility.check(
                self.sequence,
                Standard.RFC1000,
            ),
        }

    @property
    @connected
    def uses(self) -> int:
        """Report the number of uses of the part as a component in other parts.

        Returns:
            out (int): Number of parts that use this part as a component.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Retrieving usage of part '%s'.", self.uuid)

        item = call(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/parts/{self.uuid}/uses",
            ),
            RootModel[int],
        )

        logger.info(
            "Retrieved usage of part '%s': %d.",
            self.uuid,
            item.root,
        )

        return item.root

    @property
    @connected
    def twins(self) -> list[Part]:
        """List parts that are identical to this part.

        Returns:
            out (list[Part]): List of twin parts.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Fetching twins of part '%s'.", self.uuid)

        items = call(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/parts/{self.uuid}/twins",
            ),
            RootModel[list[Part]],
        )

        for item in items.root:
            item.client = self.client

        logger.info(
            "Fetched %d twins of part '%s'.",
            len(items.root) - 1,
            self.uuid,
        )

        return [item for item in items.root if item.uuid != self.uuid]

    @model_validator(mode="before")
    @classmethod
    def extract_type_uuid(cls, data: dict) -> dict:
        """Extract nested type data from raw API response.

        Converts `type` field from the raw API response into a `typeUUID`
        field.

        Args:
            data (dict): Raw data response from the API.

        Returns:
            out (dict): Normalized data with a `typeUUID` field.

        """
        if (
            "type" in data
            and isinstance(data["type"], dict)
            and "uuid" in data["type"]
        ):
            data["typeUUID"] = data["type"]["uuid"]
            data.pop("type")
        return data

    @field_validator("type", mode="before")
    @classmethod
    def convert_type(cls, value: str) -> Type:
        """Convert a type UUID to a `Type` instance.

        Args:
            value (str): The UUID of the type.

        Returns:
            out (Type): The corresponding `Type` instance.

        """
        return Type.from_uuid(value)

    @field_validator("categories", mode="before")
    @classmethod
    def convert_categories(cls, value: list[str]) -> list[Category]:
        """Convert a list of category UUIDs to `Category` instances.

        Args:
            value (list[str]): The list of category UUIDs.

        Returns:
            out (list[Category]): The corresponding `Category` instances.

        """
        return [Category.from_uuid(uuid) for uuid in value]

    @field_validator("license", mode="before")
    @classmethod
    def convert_license(cls, value: str) -> License:
        """Convert a license UUID to a `License` instance.

        Args:
            value (str): The UUID of the license.

        Returns:
            out (License): The corresponding `License` instance.

        """
        return License.from_uuid(value)

    @field_validator("sequence", mode="before")
    @classmethod
    def convert_sequence(cls, value: str) -> Seq:
        """Convert a raw sequence string to a `Seq` object.

        Args:
            value (str): The raw sequence string.

        Returns:
            out (Seq): The corresponding `Seq` object.

        """
        return Seq(value)

    @model_validator(mode="after")
    def validate_name_and_slug(self) -> Self:
        """Validate that the slug and name are consistent.

        Raises:
            InputValidationError: If the slug and name do not match.

        """
        if (
            self.slug is not None
            and self.name is not None
            and self.slug != self.name.lower().replace("_", "-")
        ):
            msg = f"Slug '{self.slug}' and name '{self.name}' do not match."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e
        return self

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4) -> UUID4:
        """Normalize the part UUID to a UUID4 instance.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4): Unique part identifier.

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

    @field_validator("categories", mode="after")
    @classmethod
    def is_category_unique(
        cls,
        value: Sequence[Category],
    ) -> Sequence[Category]:
        """Ensure that categories are unique.

        Args:
            value (Sequence[Category]): List of categories.

        Returns:
            out (Sequence[Category]): The same list of categories if valid.

        Raises:
            InputValidationError: If duplicate categories are found.

        """
        if len(value) != len(set(value)):
            msg = "Categories must be unique."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e
        return value

    @field_serializer("sequence", mode="plain")
    def serialize_sequence(self, value: Seq) -> str:
        """Serialize the sequence to a string.

        Args:
            value (Seq): The sequence to serialize.

        Returns:
            out (str): The serialized sequence string.

        """
        return str(value)

    @connected
    def load_composition(self) -> list[Reference | Seq]:
        """Load the composition of the part.

        Returns:
            out (list[Reference | Seq]): The composition of the part.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Loading composition of part '%s'.", self.uuid)

        if not self.sequence:
            msg = "Part sequence is not available."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e

        items, _ = call_paginated(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/parts/{self.uuid}/composition",
            ),
            Annotation,
        )

        position: int = 0
        composition: list[Reference | Seq] = []

        for item in items:
            start, end = item.start - 1, item.end  # Zero-indexed [start, end)
            if position < start:
                composition.append(self.sequence[position:start])
            composition.append(
                Reference(
                    uuid=item.uuid,
                    slug=item.label.lower().replace("_", "-"),
                ),
            )
            position = end

        if position < len(self.sequence):
            composition.append(self.sequence[position:])

        logger.info(
            "Loaded composition of part '%s' with %d elements.",
            self.uuid,
            len(composition),
        )

        self.composition = composition
        return composition

    @connected
    def load_authors(self) -> list[Author]:
        """Load authors of the part.

        Returns:
            out (list[Author]): List of associated authors.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Loading authors of part '%s'.", self.uuid)

        items, meta = call_paginated(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/parts/{self.uuid}/authors",
            ),
            Author,
            list[Organisation],
        )

        orgmap = {org.uuid: org for org in meta}

        for item in items:
            item.account.client = self.client
            item.organisation = orgmap[item.organisation.uuid]
            item.organisation.client = self.client

        logger.info(
            "Loaded %d authors of part '%s'.",
            len(items),
            self.uuid,
        )

        self.authors = items
        return items

    @connected
    def load_annotations(self) -> list[Annotation]:
        """Load annotations of the part.

        Returns:
            out (list[Annotation]): List of sequence annotations.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Loading annotations of part '%s'.", self.uuid)

        items, _ = call_paginated(
            self.client,
            requests.Request(
                method="GET",
                url=f"{self.client.base}/parts/{self.uuid}/sequence-features",
            ),
            Annotation,
        )

        logger.info(
            "Loaded %d annotations of part '%s'.",
            len(items),
            self.uuid,
        )

        self.annotations = items
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
        progress: Callable | None = None,
    ) -> list[Self]:
        """List parts in the Registry.

        Args:
            client (Client): Registry API client used to perform requests.
            sort (Literal): Field to sort the parts by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of parts to retrieve.
                If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Part]): Parts from the Registry.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        logger.info("Fetching parts from the Registry.")

        items, _ = call_paginated(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/parts",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            cls,
            limit=limit,
            progress=progress,
        )

        logger.info("Fetched %d parts from the Registry.", len(items))

        for item in items:
            item.client = client
        return items

    @classmethod
    @connected
    def search(
        cls,
        client: Client,
        query: str,
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
        progress: Callable | None = None,
    ) -> list[Self]:
        """Fetch parts matching a search query.

        Args:
            client (Client): Registry API client used to perform requests.
            search (str): The search query string.
            sort (Literal): Field to sort the parts by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of parts to retrieve.
                If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Part]): Parts matching the search query.

        Raises:
            NotAuthenticatedError: If the client is in anonymous mode.

        """
        logger.info("Searching parts in the Registry with query: %s", query)

        items, _ = call_paginated(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/parts",
                params={
                    "search": query,
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            cls,
            limit=limit,
            progress=progress,
        )

        logger.info(
            "Found %d parts in the Registry matching query: %s",
            len(items),
            query,
        )

        for item in items:
            item.client = client
        return items

    @classmethod
    @connected
    def get(cls, client: Client, ref: Reference) -> Self:
        """Retrieve a part by its reference.

        Args:
            client (Client): Registry API client used to perform requests.
            ref (Reference): Reference to the part, identified by either its
                UUID or slug.

        Returns:
            out (Part): The requested part.

        Raises:
            NotConnectedError: If the client is in offline mode.
            InputValidationError: If the reference is incomplete.

        """
        if ref.uuid:
            logger.info("Retrieving part by UUID: %s", ref.uuid)
            item = call(
                client,
                requests.Request(
                    method="GET",
                    url=f"{client.base}/parts/{ref.uuid}",
                ),
                cls,
            )
        elif ref.slug:
            logger.info("Retrieving part by slug: %s", ref.slug)
            item = call(
                client,
                requests.Request(
                    method="GET",
                    url=f"{client.base}/parts/slugs/{ref.slug}",
                ),
                cls,
            )
        else:
            msg = "Incomplete reference, missing slug or uuid."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e

        logger.info("Retrieved part: %s", item.uuid)

        item.client = client
        return item
