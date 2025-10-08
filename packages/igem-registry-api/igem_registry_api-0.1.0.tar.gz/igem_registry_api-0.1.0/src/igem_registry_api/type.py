"""Part type models and lookups.

This submodule defines the `Type` model used to classify Registry parts.
All defined types are available for fast local lookup as class constants.

Exports:
    Type: Model representing a part type.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, ClassVar
from uuid import UUID

import requests
from pydantic import (
    UUID4,
    Field,
    NonNegativeInt,
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
    "Type",
]


class Type(LockedModel):
    """Part type.

    Represents a type used to classify Registry parts. Available types are
    defined as class constants (e.g. `Type.PLASMID`) and stored in an in-memory
    catalog for direct use in code.

    Types can be resolved locally via `from_uuid()` or `from_id()`, or
    retrieved remotely through the API using `fetch()` and `get()`.

    Attributes:
        uuid (str | UUID4): Unique type identifier (version-4 UUID).
        slug (str | None): URL-friendly identifier for the type.
        name (str | None): Name of the type.
        description (str | None): Brief description of the type.

    Examples:
        Access a predefined type:

        ```python
        from igem_registry_api import Type

        typ = Type.PLASMID
        print(typ.uuid, typ.name)
        ```

        Resolve types from the in-memory catalog:
        ```python
        from igem_registry_api import Type

        typ1 = Type.from_id("plasmid")
        typ2 = Type.from_uuid("8ac2d621-12cf-4aec-9b88-a78250438517")

        print(typ1 is typ2)
        ```

        Retrieve types from the Registry API:
        ```python
        from igem_registry_api import Client, Type

        client = Client()
        client.connect()

        types = Type.fetch(client, limit=5)
        print(Type.get(client, types[0].uuid))
        ```

    """

    uuid: Annotated[
        str | UUID4,
        Field(
            title="UUID",
            description="Unique identifier for the part type.",
        ),
    ]

    slug: Annotated[
        str | None,
        Field(
            title="Slug",
            description="The URL-friendly identifier for the part type.",
        ),
    ] = None

    name: Annotated[
        str | None,
        Field(
            title="Name",
            description="Name of the part type.",
            alias="label",
        ),
    ] = None

    description: Annotated[
        str | None,
        Field(
            title="Description",
            description="A brief description of the part type.",
        ),
    ] = None

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4) -> UUID4:
        """Normalize the type UUID to a UUID4 instance.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4): Unique type identifier.

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
        """Resolve a type from its UUID.

        Accepts both `str` and `UUID4` objects for usability, normalizes to a
        v4 UUID string, and looks it up from the in-memory catalog.

        Args:
            uuid (str | UUID4): Unique type identifier.

        Returns:
            out (Type): Matching type.

        Raises:
            NotFoundError: If no type exists for the given UUID.

        """
        key = str(UUID(uuid, version=4) if isinstance(uuid, str) else uuid)
        logger.debug("Resolving type by uuid: %s.", key)
        try:
            return cls.CATALOG[key]
        except KeyError as e:
            raise NotFoundError(item="type", key="uuid", value=key) from e

    @classmethod
    def from_id(cls, identifier: str) -> Self:
        """Resolve a type from its slug.

        Args:
            identifier (str): Type slug.

        Returns:
            out (Type): Matching type.

        Raises:
            NotFoundError: If no type exists for the given slug.

        """
        key = identifier
        logger.debug("Resolving type by slug: %s.", key)
        try:
            return cls.CATALOG[key]
        except KeyError as e:
            raise NotFoundError(item="type", key="slug", value=key) from e

    @classmethod
    @connected
    def fetch(
        cls,
        client: Client,
        *,
        sort: Literal[
            "uuid",
            "label",
            "slug",
        ] = "label",
        order: Literal["asc", "desc"] = "asc",
        limit: NonNegativeInt | None = None,
        progress: Progress | None = None,
    ) -> list[Self]:
        """List part types from the Registry.

        Args:
            client (Client): Registry API client used to perform requests.
            sort (Literal): Field to sort the types by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of types to
                retrieve. If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Type]): Part types.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Fetching types.")

        items, _ = call_paginated(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/parts/types",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            cls,
            limit=limit,
            progress=progress,
        )

        logger.info("Fetched %d types.", len(items))

        return items

    @classmethod
    @connected
    def get(cls, client: Client, uuid: UUID4 | str) -> Self:
        """Retrieve a part type by its UUID.

        Args:
            client (Client): Registry API client used to perform requests.
            uuid (str | UUID4): Unique type identifier.

        Returns:
            out (Type): Requested type.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Retrieving type: %s.", uuid)

        item = call(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/parts/types/{uuid}",
            ),
            cls,
        )

        logger.info("Retrieved type: %s.", uuid)

        return item

    CATALOG: ClassVar[dict[str, Self]]

    TERMINATOR: ClassVar[Self]
    RBS: ClassVar[Self]
    DNA: ClassVar[Self]
    CODING: ClassVar[Self]
    REPORTER: ClassVar[Self]
    REGULATORY: ClassVar[Self]
    RNA: ClassVar[Self]
    GENERATOR: ClassVar[Self]
    INVERTER: ClassVar[Self]
    INTERMEDIATE: ClassVar[Self]
    SIGNALLING: ClassVar[Self]
    MEASUREMENT: ClassVar[Self]
    TRANSLATIONAL_UNIT: ClassVar[Self]
    PLASMID_BACKBONE: ClassVar[Self]
    PRIMER: ClassVar[Self]
    CELL: ClassVar[Self]
    DEVICE: ClassVar[Self]
    PLASMID: ClassVar[Self]
    CONJUGATION: ClassVar[Self]
    T7: ClassVar[Self]
    PROTEIN_DOMAIN: ClassVar[Self]
    SCAR: ClassVar[Self]
    PROMOTER: ClassVar[Self]
    MISCELLANEOUS: ClassVar[Self]


Type.TERMINATOR = Type(
    uuid=UUID("828126a4-2ae9-47ce-9079-42ad82a62d32"),
    slug="terminator",
    name="Terminator",
    description=(
        "A nucleic acid sequence that marks the end of a gene or operon "
        "in genomic DNA during transcription. Terminators include "
        "rho-dependent and rho-independent terminators in prokaryotes, as "
        "well as polyadenylation signals and poly(A)-independent "
        "terminators in eukaryotes."
    ),
)
Type.RBS = Type(
    uuid=UUID("9136e5fb-7232-4992-b828-d4fa4889ce63"),
    slug="rbs",
    name="RBS",
    description=(
        "A nucleic acid sequence upstream of the start codon of an mRNA "
        "transcript that is responsible for the recruitment of a ribosome "
        "during the initiation of translation. RBS can refer to a "
        "Shine-Dalgarno in prokaryotes or an internal ribosome entry site "
        "(IRES) in eukaryotes. This part type also includes mammalian "
        "translation initiation motif, the kozak sequence."
    ),
)
Type.DNA = Type(
    uuid=UUID("b252b723-460a-4b72-8eb0-de389932de00"),
    slug="dna",
    name="DNA",
    description=(
        "A nucleic acid sequence that represents a functional DNA element "
        "and is not otherwise classified. This includes restriction "
        "enzyme recognition sites, multiple cloning sites, primer binding "
        "sites, spacer sequences, origins of replication, DNA barcodes, "
        "transposons, as well as DNA with defined secondary and tertiary "
        "structures, such as DNA aptamers or DNA origami parts."
    ),
)
Type.CODING = Type(
    uuid=UUID("a797873a-d73a-454d-9c03-ee5dd5974980"),
    slug="coding",
    name="Coding",
    description=(
        "A nucleic acid sequence that encodes a protein or a peptide. "
        "Coding sequences (CDS) should begin with a start codon (3'-ATG) "
        "and end with a double stop (TAATAA-5')."
    ),
)
Type.REPORTER = Type(
    uuid=UUID("0a6e2d17-78fd-42f3-836c-181d545cfe27"),
    slug="reporter",
    name="Reporter",
    description=(
        "A nucleic acid sequence that represents a reporter device. "
        "Typically, this part type includes a coding sequence (CDS) for "
        "a fluorescent protein acting as an indicator of the desired "
        "biological activity. Can be constitutively expressed or "
        "inducible."
    ),
)
Type.REGULATORY = Type(
    uuid=UUID("324e9810-8719-4dd8-8c39-989a015a96a1"),
    slug="regulatory",
    name="Regulatory",
    description=(
        "A nucleic acid sequence that regulates the expression of a gene. "
        "Typically, this part type includes enhancers, silencers, and "
        "insulators."
    ),
)
Type.RNA = Type(
    uuid=UUID("258808a8-f859-4f0f-a1b9-17e591020eb8"),
    slug="rna",
    name="RNA",
    description=(
        "A nucleic acid sequence that represents a functional RNA element "
        "and is not otherwise classified. This includes ribozymes, "
        "riboswitches, untranslated regions (UTRs) that influence "
        "translation, small interfering RNAs (siRNAs), microRNAs "
        "(miRNAs), long non-coding RNAs (lncRNAs), guide RNAs (gRNA), RNA "
        "aptamers, and other RNA sequences with specific regulatory or "
        "structural roles."
    ),
)
Type.GENERATOR = Type(
    uuid=UUID("4a83aa73-05f2-4c21-8b0f-80e325daceda"),
    slug="generator",
    name="Generator",
    description=(
        "A nucleic acid sequence that represents a protein generator "
        "device. Typically, generators comprise a promoter, a ribosome "
        "binding site (RBS), a coding sequence (CDS), and a terminator."
    ),
)
Type.INVERTER = Type(
    uuid=UUID("0eb9e8c5-5e40-4bdf-a405-cbcd69e50e7d"),
    slug="inverter",
    name="Inverter",
    description=(
        "A nucleic acid sequence that represents a genetic inverter "
        "device, capable of reversing the expression of a gene. "
        "This part type typically comprises a protein generator for a "
        "transcriptional repressor."
    ),
)
Type.INTERMEDIATE = Type(
    uuid=UUID("28abb4c8-7237-462c-a904-bb722692e0ff"),
    slug="intermediate",
    name="Intermediate",
    description=(
        "A nucleic acid sequence that serves as a construction "
        "intermediate created during the assembly of a composite part, "
        "but that has no specific purpose or function on its own."
    ),
)
Type.SIGNALLING = Type(
    uuid=UUID("c0495fda-9566-42c7-b9e8-75a04f53dbd3"),
    slug="signalling",
    name="Signalling",
    description=(
        "A nucleic acid sequence that encodes a signaling device, "
        "enabling biological communication across or within cells. "
        "This part type typically includes senders and receivers."
    ),
)
Type.MEASUREMENT = Type(
    uuid=UUID("495a25e5-f788-4bd2-899c-2f4b3e503525"),
    slug="measurement",
    name="Measurement",
    description=(
        "A nucleic acid sequence that encodes a measurement device, "
        "designed for the quantitative characterization of biological "
        "signals or processes. This part type is typically used to "
        "evaluate the relative activity of regulatory elements under "
        "defined conditions."
    ),
)
Type.TRANSLATIONAL_UNIT = Type(
    uuid=UUID("a5e00389-c83b-410d-adee-048df3ecaf84"),
    slug="translational-unit",
    name="Translational Unit",
    description=(
        "A nucleic acid sequence composed of a ribosome binding site "
        "(RBS) and a coding sequence (CDS), that typically ends with a "
        "(double) stop codon."
    ),
)
Type.PLASMID_BACKBONE = Type(
    uuid=UUID("6c416322-36f4-4348-8ebc-3ee82622a000"),
    slug="plasmid-backbone",
    name="Plasmid Backbone",
    description=(
        "A nucleic acid sequence that is part of a plasmid, typically "
        "including the origin of replication (ori) and antibiotic "
        "resistance genes, that begins with the BioBrick suffix and "
        "ends with the BioBrick prefix."
    ),
)
Type.PRIMER = Type(
    uuid=UUID("e4bfbdbc-c096-4dfb-aae2-634204149ef2"),
    slug="primer",
    name="Primer",
    description=(
        "A short nucleic acid sequence that provides a starting point for "
        "DNA synthesis."
    ),
)
Type.CELL = Type(
    uuid=UUID("c27b7035-c0b7-4d78-a90f-89dfdae571e6"),
    slug="cell",
    name="Cell",
    description=(
        "A biological chassis represented as a host cell strain. "
        "These parts denote commonly used laboratory E. coli strains, "
        "serving as foundational systems for the expression and testing "
        "of genetic parts and devices."
    ),
)
Type.DEVICE = Type(
    uuid=UUID("6c8acd81-d083-4f0c-9601-181ef22497d9"),
    slug="device",
    name="Device",
    description=(
        "A nucleic acid sequence that encodes a genetic device, "
        "acting as a functional unit for information processing "
        "or control. This type also serves as a general class for "
        "devices not otherwise specified."
    ),
)
Type.PLASMID = Type(
    uuid=UUID("8ac2d621-12cf-4aec-9b88-a78250438517"),
    slug="plasmid",
    name="Plasmid",
    description=(
        "A nucleic acid sequence, that represents an extrachromosomal DNA "
        "molecule within a cell capable of independent replication."
        "Typically composed of a plasmid backbone and a protein generator "
        "comprising a promoter, a ribosome binding site (RBS), a coding "
        "sequence (CDS), and a terminator."
    ),
)
Type.CONJUGATION = Type(
    uuid=UUID("5b12b3f8-a959-4503-9e62-40a4bd38626a"),
    slug="conjugation",
    name="Conjugation",
    description=(
        "A nucleic acid sequence that facilitates the horizontal transfer "
        "of genetic material between bacterial cells through direct "
        "contact, like an origin of transfer (OriT) for initiating "
        "conjugation or transfer genes (Tra) encoding proteins required "
        "to form a pilus."
    ),
)
Type.T7 = Type(
    uuid=UUID("2fabb627-e479-45b1-853d-623edf20802c"),
    slug="t7",
    name="T7",
    description=(
        "A biological chassis represented by bacteriophage T7. "
        "This part type reflects the use of T7 phage as a model system "
        "and expression platform, notable for the testing of genetic "
        "parts and devices."
    ),
)
Type.PROTEIN_DOMAIN = Type(
    uuid=UUID("e4156669-594b-4100-8df9-af208b8e8c97"),
    slug="protein-domain",
    name="Protein Domain",
    description=("A nucleic acid sequence that encodes a part of a protein."),
)
Type.SCAR = Type(
    uuid=UUID("9e0c5a67-0a07-48fd-ace3-e94e06820291"),
    slug="scar",
    name="Scar",
    description=(
        "A nucleic acid sequence that is a scar left after the assembly "
        "of a composite part, typically resulting from the use of "
        "restriction enzymes and ligation."
    ),
)
Type.PROMOTER = Type(
    uuid=UUID("0f026097-b490-41eb-b042-78316fc4f218"),
    slug="promoter",
    name="Promoter",
    description=(
        "A nucleic acid sequence that initiates transcription of a gene, "
        "typically a promoter that recruits transcriptional machinery and "
        "leads to transcription of the downstream DNA sequence. This part "
        "type also includes RNA promoters involved in RNA replication."
    ),
)
Type.MISCELLANEOUS = Type(
    uuid=UUID("56828cb1-3c65-4833-bd2c-dcdddd8d043b"),
    slug="miscellaneous",
    name="Miscellaneous",
    description=(
        "A part that does not fit into any other category, due to its "
        "unique or undefined functions."
    ),
)

Type.CATALOG = {
    str(key): value
    for value in [
        Type.TERMINATOR,
        Type.RBS,
        Type.DNA,
        Type.CODING,
        Type.REPORTER,
        Type.REGULATORY,
        Type.RNA,
        Type.GENERATOR,
        Type.INVERTER,
        Type.INTERMEDIATE,
        Type.SIGNALLING,
        Type.MEASUREMENT,
        Type.TRANSLATIONAL_UNIT,
        Type.PLASMID_BACKBONE,
        Type.PRIMER,
        Type.CELL,
        Type.DEVICE,
        Type.PLASMID,
        Type.CONJUGATION,
        Type.T7,
        Type.PROTEIN_DOMAIN,
        Type.SCAR,
        Type.PROMOTER,
        Type.MISCELLANEOUS,
    ]
    for key in (value.uuid, value.slug)
}
