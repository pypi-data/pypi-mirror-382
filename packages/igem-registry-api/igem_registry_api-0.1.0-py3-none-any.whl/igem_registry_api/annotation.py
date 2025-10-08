"""Sequence feature annotations.

This submodule defines classes related to sequence annotations on parts. It
provides the `Annotation` model for representing annotations, along with
the `Strand` and `Form` enums for strand orientation and feature types
respectively.

Exports:
    Annotation: Model representing a sequence annotation.
    Form: Enum of sequence annotation types.
    Strand: Enum of strand orientations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from pydantic import (
    UUID4,
    Field,
    field_validator,
    model_validator,
)

from igem_registry_api.errors import InputValidationError

from .schemas import CleanEnum, DynamicModel

if TYPE_CHECKING:
    from typing import Self

__all__: list[str] = [
    "Annotation",
    "Form",
    "Strand",
]


class Strand(CleanEnum):
    """Strand orientation.

    Defines the strand orientation of a sequence annotation.

    Attributes:
        FORWARD: Feature lies on the forward (5' to 3') strand.
        REVERSE: Feature lies on the reverse (3' to 5') strand.

    """

    FORWARD = "forward"
    REVERSE = "reverse"


class Form(CleanEnum):
    """Forms of sequence annotations.

    Defines the controlled vocabulary for sequence annotation types.

    Attributes:
        CODING_CDS: Coding sequence.
        CODING_STARTCODON: Start codon.
        CODING_STOPCODON: Stop codon.
        CODING_TAG: Protein tag.
        CODING_REPORTER: Reporter protein.

        REGULATORY_PROMOTER: Promoter.
        REGULATORY_RBS: Ribosome binding site.
        REGULATORY_TERMINATOR: Transcription terminator.
        REGULATORY_OPERATOR: Operator site.
        REGULATORY_ENHANCER: Enhancer element.
        REGULATORY_ATTENUATOR: Attenuator element.
        REGULATORY_INSULATOR: Insulator element.
        REGULATORY_POLYASIGNAL: Polyadenylation signal.

        ASSEMBLY_SCAR: Assembly scar.
        ASSEMBLY_PREFIX: Assembly prefix.
        ASSEMBLY_SUFIX: Assembly suffix.
        ASSEMBLY_RESTRICTIONSITE: Restriction enzyme site.
        ASSEMBLY_BARCODE: DNA barcode.
        ASSEMBLY_BIOBRICK: BioBrick prefix/suffix region.

        OTHER_MISCELLANEOUS: Miscellaneous feature.
        OTHER_REPEATREGION: Repeat region.
        OTHER_ORIGINOFREPLICATION: Origin of replication.
        OTHER_PRIMERBINDINGSITE: Primer binding site.
        OTHER_PROTEINBINDINGSITE: Protein binding site.
        OTHER_MUTATION: Mutation.
        OTHER_SILENTMUTATION: Silent mutation.
        OTHER_CONSERVEDREGION: Conserved region.
        OTHER_STEMLOOP: Stem-loop region.

    """

    CODING_CDS = "coding:cds"
    CODING_STARTCODON = "coding:start-codon"
    CODING_STOPCODON = "coding:stop-codon"
    CODING_TAG = "coding:tag"
    CODING_REPORTER = "coding:reporter"

    REGULATORY_PROMOTER = "regulatory:promoter"
    REGULATORY_RBS = "regulatory:rbs"
    REGULATORY_TERMINATOR = "regulatory:terminator"
    REGULATORY_OPERATOR = "regulatory:operator"
    REGULATORY_ENHANCER = "regulatory:enhancer"
    REGULATORY_ATTENUATOR = "regulatory:attenuator"
    REGULATORY_INSULATOR = "regulatory:insulator"
    REGULATORY_POLYASIGNAL = "regulatory:polya-signal"

    ASSEMBLY_SCAR = "assembly:scar"
    ASSEMBLY_PREFIX = "assembly:prefix"
    ASSEMBLY_SUFIX = "assembly:sufix"
    ASSEMBLY_RESTRICTIONSITE = "assembly:restriction-site"
    ASSEMBLY_BARCODE = "assembly:barcode"
    ASSEMBLY_BIOBRICK = "assembly:biobrick"

    OTHER_MISCELLANEOUS = "other:miscellaneous"
    OTHER_REPEATREGION = "other:repeat-region"
    OTHER_ORIGINOFREPLICATION = "other:origin-of-replication"
    OTHER_PRIMERBINDINGSITE = "other:primer-binding-site"
    OTHER_PROTEINBINDINGSITE = "other:protein-binding-site"
    OTHER_MUTATION = "other:mutation"
    OTHER_SILENTMUTATION = "other:silent-mutation"
    OTHER_CONSERVEDREGION = "other:conserved-region"
    OTHER_STEMLOOP = "other:stem-loop"


class Annotation(DynamicModel):
    """Sequence annotation.

    Represents a sequence annotation of a part in the Registry. An `Annotation`
    stores details about the feature type, location, and strand orientation.

    Attributes:
        uuid (str | UUID4 | None): Unique author identifier (version-4 UUID).
        form (Form): Type of sequence annotation.
        label (str | None): Label of the annotation.
        strand (Strand): Strand orientation of the annotation.
        start (int): Start of the annotation (zero-indexed, inclusive).
        end (int): End of the annotation (zero-indexed, exclusive).

    Examples:
        Create an `Annotation` instance:

        ```python
        from igem_registry_api import Annotation, Form, Strand

        feature = Annotation(
            form=Form.CODING_CDS,
            label="GFP",
            strand=Strand.FORWARD,
            start=0,
            end=717,
        )
        ```

    """

    uuid: Annotated[
        str | UUID4 | None,
        Field(
            title="UUID",
            description="Unique identifier for the annotation.",
            frozen=True,
        ),
    ] = None
    form: Annotated[
        Form,
        Field(
            title="Form",
            description="Type of sequence annotation.",
            alias="type",
            frozen=False,
        ),
    ]
    label: Annotated[
        str,
        Field(
            title="Label",
            description="Label of the annotation.",
            max_length=20,
            frozen=False,
        ),
    ]
    strand: Annotated[
        Strand,
        Field(
            title="Strand",
            description="Strand orientation of the annotation.",
            frozen=False,
        ),
    ]
    start: Annotated[
        int,
        Field(
            title="Start",
            description="Start of the annotation (zero-indexed, inclusive).",
            frozen=False,
        ),
    ]
    end: Annotated[
        int,
        Field(
            title="End",
            description="End of the annotation (zero-indexed, exclusive).",
            ge=1,
            frozen=False,
        ),
    ]

    @model_validator(mode="before")
    @classmethod
    def extract_composite(cls, data: dict) -> dict:
        """Extract annotation data from composite part input.

        Pulls out relevant fields from a composite part representation and
        maps them to the `Annotation` model fields.

        Args:
            data (dict): Raw data response from the API.

        Returns:
            out (dict): Extracted annotation data.

        """
        if "componentUUID" in data and "componentName" in data:
            data["label"] = data.pop("componentName")
            data["uuid"] = data.pop("componentUUID")
            data["form"] = Form.OTHER_MISCELLANEOUS
        return data

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4 | None) -> UUID4 | None:
        """Normalize the annotation UUID to a UUID4 instance, if provided.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4 | None): Unique annotation identifier.

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

    @model_validator(mode="after")
    def ensure_position(self) -> Self:
        """Ensure the annotation position is valid.

        Validates that the provided start and end positions of the annotation
        are not identical.

        Raises:
            InputValidationError: If the start and end positions are identical.

        """
        if self.start == self.end:
            msg = "Annotation start and end cannot be identical."
            e = ValueError(msg)
            raise InputValidationError(error=e) from e
        return self
