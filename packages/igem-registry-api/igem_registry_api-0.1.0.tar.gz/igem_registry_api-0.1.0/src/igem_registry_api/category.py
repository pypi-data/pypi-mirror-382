"""Part category models and lookups.

This submodule defines the `Category` model used to categorize Registry parts.
All defined categories are available for fast local lookup as class constants.

Exports:
    Category: Model representing a part category.
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
    "Category",
]


class Category(LockedModel):
    """Part category.

    Represents a category used to organise Registry parts. Available categories
    are defined as class constants (e.g. `Category.BIOSAFETY_KILL_SWITCH`)
    and stored in an in-memory catalog for direct use in code.

    Categories can be resolved locally via `from_uuid()` or `from_id()`, or
    retrieved remotely through the API using `fetch()` and `get()`.

    Attributes:
        uuid (str | UUID4): Unique category identifier (version-4 UUID).
        label (str | None): Label for the category.
        value (str | None): Registry internal value of the category.
        description (str | None): Brief description of the category.

    Examples:
        Access a predefined category:

        ```python
        from igem_registry_api import Category

        cat = Category.BIOSAFETY_KILL_SWITCH
        print(cat.uuid, cat.label)
        ```

        Resolve categories from the in-memory catalog:
        ```python
        from igem_registry_api import Category

        cat1 = Category.from_id("//biosafety/kill_switch")
        cat2 = Category.from_uuid("1f80037e-36a3-42ca-b439-7085bf45e3c9")

        print(cat1 is cat2)
        ```

        Retrieve categories from the Registry API:
        ```python
        from igem_registry_api import Category, Client

        client = Client()
        client.connect()

        categories = Category.fetch(client, limit=5)
        print(Category.get(client, categories[0].uuid))
        ```

    """

    uuid: Annotated[
        str | UUID4,
        Field(
            title="UUID",
            description="Unique identifier for the part category.",
        ),
    ]

    label: Annotated[
        str | None,
        Field(
            title="Label",
            description="Label of the part category.",
            pattern=r"^(\/\/)?[a-z0-9_]+(\/[a-z0-9_]+){0,3}$",
        ),
    ] = None

    value: Annotated[
        str | None,
        Field(
            title="Value",
            description="Value of the part category.",
        ),
    ] = None

    description: Annotated[
        str | None,
        Field(
            title="Description",
            description="Brief description of the part category.",
        ),
    ] = None

    @field_validator("uuid", mode="after")
    @classmethod
    def ensure_uuid(cls, value: str | UUID4) -> UUID4:
        """Normalize the category UUID to a UUID4 instance.

        Accepts both `str` and `UUID4` objects for usability, while ensuring
        the stored value is always a `UUID4`. This avoids type checking errors
        when a `str` input is provided.

        Args:
            value (str | UUID4): Unique category identifier.

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
        """Resolve a category from its UUID.

        Accepts both `str` and `UUID4` objects for usability, normalizes to a
        v4 UUID string, and looks it up from the in-memory catalog.

        Args:
            uuid (str | UUID4): Unique category identifier.

        Returns:
            out (Category): Matching category.

        Raises:
            NotFoundError: If no category exists for the given UUID.

        """
        key = str(UUID(uuid, version=4) if isinstance(uuid, str) else uuid)
        logger.debug("Resolving category by uuid: %s.", key)
        try:
            return cls.CATALOG[key]
        except KeyError as e:
            raise NotFoundError(item="category", key="uuid", value=key) from e

    @classmethod
    def from_id(cls, identifier: str) -> Self:
        """Resolve a category from its label.

        Args:
            identifier (str): Category label.

        Returns:
            out (Category): Matching category.

        Raises:
            NotFoundError: If no category exists for the given label.

        """
        key = identifier
        logger.debug("Resolving category by label: %s.", key)
        try:
            return cls.CATALOG[key]
        except KeyError as e:
            raise NotFoundError(item="category", key="label", value=key) from e

    @classmethod
    @connected
    def fetch(
        cls,
        client: Client,
        *,
        sort: Literal[
            "uuid",
            "label",
            "value",
            "description",
        ] = "label",
        order: Literal["asc", "desc"] = "asc",
        limit: NonNegativeInt | None = None,
        progress: Progress | None = None,
    ) -> list[Self]:
        """List part categories from the Registry.

        Args:
            client (Client): Registry API client used to perform requests.
            sort (Literal): Field to sort the categories by.
            order (Literal): Sorting order, either ascending or descending.
            limit (NonNegativeInt | None): Maximum number of categories to
                retrieve. If `None`, fetches all available.
            progress (Progress | None): Callback function to report progress.

        Returns:
            out (list[Category]): Part categories.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Fetching categories.")

        items, _ = call_paginated(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/parts/categories",
                params={
                    "orderBy": sort,
                    "order": order.upper(),
                },
            ),
            cls,
            limit=limit,
            progress=progress,
        )

        logger.info("Fetched %d categories.", len(items))

        return items

    @classmethod
    @connected
    def get(cls, client: Client, uuid: str | UUID4) -> Self:
        """Retrieve a part category by its UUID.

        Args:
            client (Client): Registry API client used to perform requests.
            uuid (str | UUID4): Unique category identifier.

        Returns:
            out (Category): Requested category.

        Raises:
            NotConnectedError: If the client is in offline mode.

        """
        logger.info("Retrieving category: %s.", uuid)

        item = call(
            client,
            requests.Request(
                method="GET",
                url=f"{client.base}/parts/categories/{uuid}",
            ),
            cls,
        )

        logger.info("Retrieved category: %s.", uuid)

        return item

    CATALOG: ClassVar[dict[str, Self]]

    BINDING_CELLULOSE: ClassVar[Self]
    BINDING_METAL: ClassVar[Self]
    BIOSAFETY: ClassVar[Self]
    BIOSAFETY_KILL_SWITCH: ClassVar[Self]
    BIOSAFETY_SEMANTIC_CONTAINMENT: ClassVar[Self]
    BIOSAFETY_XNASE: ClassVar[Self]
    CDS: ClassVar[Self]
    CDS_BIOSYNTHESIS: ClassVar[Self]
    CDS_BIOSYNTHESIS_ANTHOCYANINS: ClassVar[Self]
    CDS_CHROMATINREMODELING: ClassVar[Self]
    CDS_ENZYME: ClassVar[Self]
    CDS_ENZYME_CHROMATINREMODELING: ClassVar[Self]
    CDS_ENZYME_DNAPOLYMERASE: ClassVar[Self]
    CDS_ENZYME_DNASE: ClassVar[Self]
    CDS_ENZYME_ENDONUCLEASE: ClassVar[Self]
    CDS_ENZYME_ENDONUCLEASE_RESTRICTION: ClassVar[Self]
    CDS_ENZYME_EXONUCLEASE: ClassVar[Self]
    CDS_ENZYME_LIGASE: ClassVar[Self]
    CDS_ENZYME_LYSIS: ClassVar[Self]
    CDS_ENZYME_METHYLATION: ClassVar[Self]
    CDS_ENZYME_PHOSPHORYLATION: ClassVar[Self]
    CDS_ENZYME_PROTEASE: ClassVar[Self]
    CDS_ENZYME_RNAP: ClassVar[Self]
    CDS_ENZYME_RNAPOLYMERASE: ClassVar[Self]
    CDS_LIGAND: ClassVar[Self]
    CDS_LYSIS: ClassVar[Self]
    CDS_MEMBRANE: ClassVar[Self]
    CDS_MEMBRANE_CHANNEL: ClassVar[Self]
    CDS_MEMBRANE_EXTRACELLULAR: ClassVar[Self]
    CDS_MEMBRANE_LYSIS: ClassVar[Self]
    CDS_MEMBRANE_PUMP: ClassVar[Self]
    CDS_MEMBRANE_RECEPTOR: ClassVar[Self]
    CDS_MEMBRANE_TRANSPORTER: ClassVar[Self]
    CDS_RECEPTOR: ClassVar[Self]
    CDS_RECEPTOR_ANTIBODY: ClassVar[Self]
    CDS_REPORTER: ClassVar[Self]
    CDS_REPORTER_CFP: ClassVar[Self]
    CDS_REPORTER_CHROMOPROTEIN: ClassVar[Self]
    CDS_REPORTER_GFP: ClassVar[Self]
    CDS_REPORTER_RFP: ClassVar[Self]
    CDS_REPORTER_YFP: ClassVar[Self]
    CDS_SELECTIONMARKER: ClassVar[Self]
    CDS_SELECTIONMARKER_ANTIBIOTICRESISTANCE: ClassVar[Self]
    CDS_TRANSCRIPTIONALREGULATOR: ClassVar[Self]
    CDS_TRANSCRIPTIONALREGULATOR_ACTIVATOR: ClassVar[Self]
    CDS_TRANSCRIPTIONALREGULATOR_REPRESSOR: ClassVar[Self]
    CHASSIS: ClassVar[Self]
    CHASSIS_AFERROOXIDANS: ClassVar[Self]
    CHASSIS_BACTERIOPHAGE: ClassVar[Self]
    CHASSIS_BACTERIOPHAGE_T3: ClassVar[Self]
    CHASSIS_BACTERIOPHAGE_T4: ClassVar[Self]
    CHASSIS_BACTERIOPHAGE_T7: ClassVar[Self]
    CHASSIS_EUKARYOTE: ClassVar[Self]
    CHASSIS_EUKARYOTE_ATHALIANA: ClassVar[Self]
    CHASSIS_EUKARYOTE_HUMAN: ClassVar[Self]
    CHASSIS_EUKARYOTE_MPOLYMORPHA: ClassVar[Self]
    CHASSIS_EUKARYOTE_NBENTHAMIANA: ClassVar[Self]
    CHASSIS_EUKARYOTE_NTABACUM: ClassVar[Self]
    CHASSIS_EUKARYOTE_PICHIA: ClassVar[Self]
    CHASSIS_EUKARYOTE_PLANTS_OTHER: ClassVar[Self]
    CHASSIS_EUKARYOTE_PPATENS: ClassVar[Self]
    CHASSIS_EUKARYOTE_YEAST: ClassVar[Self]
    CHASSIS_MISCELLANEOUS: ClassVar[Self]
    CHASSIS_MULTIHOST: ClassVar[Self]
    CHASSIS_ORGANELLE: ClassVar[Self]
    CHASSIS_ORGANELLE_CHLOROPLAST: ClassVar[Self]
    CHASSIS_ORGANELLE_MITOCHONDRION: ClassVar[Self]
    CHASSIS_PROKARYOTE: ClassVar[Self]
    CHASSIS_PROKARYOTE_BCEPACIA: ClassVar[Self]
    CHASSIS_PROKARYOTE_BSUBTILIS: ClassVar[Self]
    CHASSIS_PROKARYOTE_CYANOBACTERIUM: ClassVar[Self]
    CHASSIS_PROKARYOTE_ECOLI: ClassVar[Self]
    CHASSIS_PROKARYOTE_ECOLI_NISSLE: ClassVar[Self]
    CHASSIS_PROKARYOTE_GXYLINUS: ClassVar[Self]
    CHASSIS_PROKARYOTE_LACTOBACILLUS: ClassVar[Self]
    CHASSIS_PROKARYOTE_LACTOCOCCUS: ClassVar[Self]
    CHASSIS_PROKARYOTE_MFLORUM: ClassVar[Self]
    CHASSIS_PROKARYOTE_PANANATIS: ClassVar[Self]
    CHASSIS_PROKARYOTE_PMIRABILIS: ClassVar[Self]
    CHASSIS_PROKARYOTE_PPUTIDA: ClassVar[Self]
    CHASSIS_PROKARYOTE_REUPHORA: ClassVar[Self]
    CHASSIS_PROKARYOTE_RRADIOBACTER: ClassVar[Self]
    CHASSIS_PROKARYOTE_SALMONELLA: ClassVar[Self]
    CHASSIS_PROKARYOTE_SESPANAENSIS: ClassVar[Self]
    CHASSIS_PROKARYOTE_SUBTILIS: ClassVar[Self]
    CHASSIS_PROKARYOTE_SYNECHOCYSTIS: ClassVar[Self]
    CHASSIS_PROKARYOTE_VHARVEYI: ClassVar[Self]
    CLASSIC_COMPOSITE_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_DEVICE_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_GENERATOR_PLASMIDS: ClassVar[Self]
    CLASSIC_GENERATOR_PRC: ClassVar[Self]
    CLASSIC_GENERATOR_PRCT: ClassVar[Self]
    CLASSIC_GENERATOR_RC: ClassVar[Self]
    CLASSIC_GENERATOR_RCT: ClassVar[Self]
    CLASSIC_GENERATOR_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_INTERMEDIATE_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_INVERTER_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_MEASUREMENT_O_H: ClassVar[Self]
    CLASSIC_MEASUREMENT_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_OTHER_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_PLASMID_MEASUREMENT: ClassVar[Self]
    CLASSIC_PLASMID_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_PROJECT_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_RBS_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_REGULATORY_OTHER: ClassVar[Self]
    CLASSIC_REGULATORY_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_REPORTER: ClassVar[Self]
    CLASSIC_REPORTER_CONSTITUTIVE: ClassVar[Self]
    CLASSIC_REPORTER_MULTIPLE: ClassVar[Self]
    CLASSIC_REPORTER_PRET: ClassVar[Self]
    CLASSIC_REPORTER_RET: ClassVar[Self]
    CLASSIC_RNA_UNCATEGORIZED: ClassVar[Self]
    CLASSIC_SIGNALLING_RECEIVER: ClassVar[Self]
    CLASSIC_SIGNALLING_SENDER: ClassVar[Self]
    CLASSIC_TEMPORARY_UNCATEGORIZED: ClassVar[Self]
    DIRECTION: ClassVar[Self]
    DIRECTION_BIDIRECTIONAL: ClassVar[Self]
    DIRECTION_FORWARD: ClassVar[Self]
    DIRECTION_REVERSE: ClassVar[Self]
    DNA: ClassVar[Self]
    DNA_APTAMER: ClassVar[Self]
    DNA_BIOSCAFFOLD: ClassVar[Self]
    DNA_CHROMOSOMALINTEGRATION: ClassVar[Self]
    DNA_CLONINGSITE: ClassVar[Self]
    DNA_CONJUGATION: ClassVar[Self]
    DNA_DNAZYME: ClassVar[Self]
    DNA_NUCLEOTIDE: ClassVar[Self]
    DNA_ORIGAMI: ClassVar[Self]
    DNA_ORIGIN_OF_REPLICATION: ClassVar[Self]
    DNA_PRIMERBINDINGSITE: ClassVar[Self]
    DNA_RESTRICTIONSITE: ClassVar[Self]
    DNA_SCAR: ClassVar[Self]
    DNA_SPACER: ClassVar[Self]
    DNA_TRANSPOSOME_TN5: ClassVar[Self]
    DNA_TRANSPOSON: ClassVar[Self]
    EXTREMOPHILES: ClassVar[Self]
    FUNCTION_BIOFUELS: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_AHL: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_BUTANOL: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_CELLULOSE: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_HEME: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_ISOPRENOID: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_ODORANT: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_PHYCOCYANOBILIN: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_PLASTIC: ClassVar[Self]
    FUNCTION_BIOSYNTHESIS_PYOCYANIN: ClassVar[Self]
    FUNCTION_CELLDEATH: ClassVar[Self]
    FUNCTION_CELLSIGNALLING: ClassVar[Self]
    FUNCTION_COLIROID: ClassVar[Self]
    FUNCTION_CONJUGATION: ClassVar[Self]
    FUNCTION_CRISPR: ClassVar[Self]
    FUNCTION_CRISPR_CAS: ClassVar[Self]
    FUNCTION_CRISPR_CAS9: ClassVar[Self]
    FUNCTION_CRISPR_GRNA: ClassVar[Self]
    FUNCTION_CRISPR_GRNA_CONSTRUCT: ClassVar[Self]
    FUNCTION_CRISPR_GRNA_EFFICIENT: ClassVar[Self]
    FUNCTION_CRISPR_GRNA_REPEAT: ClassVar[Self]
    FUNCTION_CRISPR_GRNA_SPACER: ClassVar[Self]
    FUNCTION_DEGRADATION: ClassVar[Self]
    FUNCTION_DEGRADATION_AHL: ClassVar[Self]
    FUNCTION_DEGRADATION_BISPHENOL: ClassVar[Self]
    FUNCTION_DEGRADATION_CELLULOSE: ClassVar[Self]
    FUNCTION_DNA: ClassVar[Self]
    FUNCTION_FRET: ClassVar[Self]
    FUNCTION_IMMUNOLOGY: ClassVar[Self]
    FUNCTION_MISMATCHREPAIR: ClassVar[Self]
    FUNCTION_MOTILITY: ClassVar[Self]
    FUNCTION_ODOR: ClassVar[Self]
    FUNCTION_RECOMBINATION: ClassVar[Self]
    FUNCTION_RECOMBINATION_CRE: ClassVar[Self]
    FUNCTION_RECOMBINATION_FIM: ClassVar[Self]
    FUNCTION_RECOMBINATION_FLP: ClassVar[Self]
    FUNCTION_RECOMBINATION_HIN: ClassVar[Self]
    FUNCTION_RECOMBINATION_LAMBDA: ClassVar[Self]
    FUNCTION_RECOMBINATION_P22: ClassVar[Self]
    FUNCTION_RECOMBINATION_XER: ClassVar[Self]
    FUNCTION_REGULATION_TRANSCRIPTIONAL: ClassVar[Self]
    FUNCTION_REPORTER: ClassVar[Self]
    FUNCTION_REPORTER_COLOR: ClassVar[Self]
    FUNCTION_REPORTER_FLUORESCENCE: ClassVar[Self]
    FUNCTION_REPORTER_LIGHT: ClassVar[Self]
    FUNCTION_REPORTER_PIGMENT: ClassVar[Self]
    FUNCTION_SENSOR: ClassVar[Self]
    FUNCTION_SENSOR_LEAD: ClassVar[Self]
    FUNCTION_SENSOR_LIGHT: ClassVar[Self]
    FUNCTION_SENSOR_METAL: ClassVar[Self]
    FUNCTION_STRUCTURES: ClassVar[Self]
    FUNCTION_TUMORKILLINGBACTERIA: ClassVar[Self]
    PLASMID: ClassVar[Self]
    PLASMIDBACKBONE: ClassVar[Self]
    PLASMIDBACKBONE_ARCHIVE: ClassVar[Self]
    PLASMIDBACKBONE_ASSEMBLY: ClassVar[Self]
    PLASMIDBACKBONE_ASSEMBLY_TYPEIIS: ClassVar[Self]
    PLASMIDBACKBONE_COMPONENT_DEFAULTINSERT: ClassVar[Self]
    PLASMIDBACKBONE_COMPONENT_SELECTIONMARKER_ANTIBIOTICRESISTANCE: ClassVar[
        Self
    ]
    PLASMIDBACKBONE_COPYNUMBER: ClassVar[Self]
    PLASMIDBACKBONE_COPYNUMBER_HIGH: ClassVar[Self]
    PLASMIDBACKBONE_COPYNUMBER_INDUCIBLE: ClassVar[Self]
    PLASMIDBACKBONE_COPYNUMBER_LOW: ClassVar[Self]
    PLASMIDBACKBONE_COPYNUMBER_MEDIUM: ClassVar[Self]
    PLASMIDBACKBONE_EXPRESSION: ClassVar[Self]
    PLASMIDBACKBONE_EXPRESSION_CONSTITUTIVE: ClassVar[Self]
    PLASMIDBACKBONE_EXPRESSION_INDUCIBLE: ClassVar[Self]
    PLASMIDBACKBONE_LIBRARYSCREENING: ClassVar[Self]
    PLASMIDBACKBONE_LIBRARYSCREENING_CODINGSEQUENCE: ClassVar[Self]
    PLASMIDBACKBONE_LIBRARYSCREENING_PROMOTER: ClassVar[Self]
    PLASMIDBACKBONE_LIBRARYSCREENING_RBSCODINGSEQUENCE: ClassVar[Self]
    PLASMIDBACKBONE_OPERATION: ClassVar[Self]
    PLASMIDBACKBONE_PROTEINFUSION: ClassVar[Self]
    PLASMIDBACKBONE_SYNTHESIS: ClassVar[Self]
    PLASMIDBACKBONE_VERSION_10: ClassVar[Self]
    PLASMIDBACKBONE_VERSION_3: ClassVar[Self]
    PLASMIDBACKBONE_VERSION_4: ClassVar[Self]
    PLASMIDBACKBONE_VERSION_5: ClassVar[Self]
    PLASMID_CHROMOSOMALINTEGRATION: ClassVar[Self]
    PLASMID_COMPONENT_CLONINGSITE: ClassVar[Self]
    PLASMID_COMPONENT_INSULATION: ClassVar[Self]
    PLASMID_COMPONENT_ORIGIN: ClassVar[Self]
    PLASMID_COMPONENT_OTHER: ClassVar[Self]
    PLASMID_COMPONENT_PRIMERBINDINGSITE: ClassVar[Self]
    PLASMID_CONSTRUCTION: ClassVar[Self]
    PLASMID_EXPRESSION: ClassVar[Self]
    PLASMID_EXPRESSION_T7: ClassVar[Self]
    PLASMID_MEASUREMENT: ClassVar[Self]
    PLASMID_SP6: ClassVar[Self]
    PRIMER_M13: ClassVar[Self]
    PRIMER_PART: ClassVar[Self]
    PRIMER_PART_AMPLIFICATION: ClassVar[Self]
    PRIMER_PART_SEQUENCING: ClassVar[Self]
    PRIMER_PLASMID_AMPLIFICATION: ClassVar[Self]
    PRIMER_REPORTER_CFP: ClassVar[Self]
    PRIMER_REPORTER_GFP: ClassVar[Self]
    PRIMER_REPORTER_YFP: ClassVar[Self]
    PRIMER_SP6: ClassVar[Self]
    PRIMER_T3: ClassVar[Self]
    PRIMER_T7: ClassVar[Self]
    PROMOTER: ClassVar[Self]
    PROMOTER_ANDERSON: ClassVar[Self]
    PROMOTER_IRON: ClassVar[Self]
    PROMOTER_LOGIC_USTC: ClassVar[Self]
    PROMOTER_STRESSKIT: ClassVar[Self]
    PROTEINDOMAIN: ClassVar[Self]
    PROTEINDOMAIN_ACTIVATION: ClassVar[Self]
    PROTEINDOMAIN_AFFINITY: ClassVar[Self]
    PROTEINDOMAIN_BINDING: ClassVar[Self]
    PROTEINDOMAIN_BINDING_CELLULOSE: ClassVar[Self]
    PROTEINDOMAIN_CLEAVAGE: ClassVar[Self]
    PROTEINDOMAIN_DEGRADATION: ClassVar[Self]
    PROTEINDOMAIN_DNABINDING: ClassVar[Self]
    PROTEINDOMAIN_HEAD: ClassVar[Self]
    PROTEINDOMAIN_INTERNAL: ClassVar[Self]
    PROTEINDOMAIN_INTERNAL_SPECIAL: ClassVar[Self]
    PROTEINDOMAIN_LINKER: ClassVar[Self]
    PROTEINDOMAIN_LOCALIZATION: ClassVar[Self]
    PROTEINDOMAIN_REPRESSION: ClassVar[Self]
    PROTEINDOMAIN_TAIL: ClassVar[Self]
    PROTEINDOMAIN_TRANSMEMBRANE: ClassVar[Self]
    RBS_PROKARYOTE: ClassVar[Self]
    RBS_PROKARYOTE_CONSTITUTIVE: ClassVar[Self]
    RBS_PROKARYOTE_CONSTITUTIVE_ANDERSON: ClassVar[Self]
    RBS_PROKARYOTE_CONSTITUTIVE_COMMUNITY: ClassVar[Self]
    RBS_PROKARYOTE_CONSTITUTIVE_CONSTITUTIVE: ClassVar[Self]
    RBS_PROKARYOTE_CONSTITUTIVE_MISCELLANEOUS: ClassVar[Self]
    RBS_PROKARYOTE_CONSTITUTIVE_RACKHAM: ClassVar[Self]
    RBS_PROKARYOTE_REGULATED_ISSACS: ClassVar[Self]
    RBS_PROKARYOTIC_CONSTITUTIVE_MISCELLANEOUS: ClassVar[Self]
    RECEIVER: ClassVar[Self]
    REGULATION: ClassVar[Self]
    REGULATION_CONSTITUTIVE: ClassVar[Self]
    REGULATION_MULTIPLE: ClassVar[Self]
    REGULATION_NEGATIVE: ClassVar[Self]
    REGULATION_POSITIVE: ClassVar[Self]
    REGULATION_UNKNOWN: ClassVar[Self]
    REGULATOR: ClassVar[Self]
    RIBOSOME: ClassVar[Self]
    RIBOSOME_EUKARYOTE: ClassVar[Self]
    RIBOSOME_EUKARYOTE_YEAST: ClassVar[Self]
    RIBOSOME_PROKARYOTE: ClassVar[Self]
    RIBOSOME_PROKARYOTE_BCEPACIA: ClassVar[Self]
    RIBOSOME_PROKARYOTE_BSUBTILIS: ClassVar[Self]
    RIBOSOME_PROKARYOTE_CUSTOM: ClassVar[Self]
    RIBOSOME_PROKARYOTE_ECOLI: ClassVar[Self]
    RIBOSOME_PROKARYOTE_PANANATIS: ClassVar[Self]
    RIBOSOME_PROKARYOTE_PPUTIDA: ClassVar[Self]
    RIBOSOME_PROKARYOTE_SALMONELLA: ClassVar[Self]
    RIBOSOME_PROKARYOTE_SESPANAENSIS: ClassVar[Self]
    RNA: ClassVar[Self]
    RNA_APTAMER: ClassVar[Self]
    RNA_APTAZYME: ClassVar[Self]
    RNAP: ClassVar[Self]
    RNAP_BACTERIOPHAGE_SP6: ClassVar[Self]
    RNAP_BACTERIOPHAGE_T3: ClassVar[Self]
    RNAP_BACTERIOPHAGE_T7: ClassVar[Self]
    RNAP_EUKARYOTE: ClassVar[Self]
    RNAP_EUKARYOTE_PICHIA: ClassVar[Self]
    RNAP_EUKARYOTE_YEAST: ClassVar[Self]
    RNAP_MISCELLANEOUS: ClassVar[Self]
    RNAP_PROKARYOTE: ClassVar[Self]
    RNAP_PROKARYOTE_AFERROOXIDANS: ClassVar[Self]
    RNAP_PROKARYOTE_ECOLI: ClassVar[Self]
    RNAP_PROKARYOTE_ECOLI_SIGMA24: ClassVar[Self]
    RNAP_PROKARYOTE_ECOLI_SIGMA25: ClassVar[Self]
    RNAP_PROKARYOTE_ECOLI_SIGMA32: ClassVar[Self]
    RNAP_PROKARYOTE_ECOLI_SIGMA54: ClassVar[Self]
    RNAP_PROKARYOTE_ECOLI_SIGMA70: ClassVar[Self]
    RNAP_PROKARYOTE_ECOLI_SIGMAS: ClassVar[Self]
    RNAP_PROKARYOTE_PMIRABILIS: ClassVar[Self]
    RNAP_PROKARYOTE_PPUTIDA: ClassVar[Self]
    RNAP_PROKARYOTE_REUPHORA: ClassVar[Self]
    RNAP_PROKARYOTE_SALMONELLA: ClassVar[Self]
    RNAP_PROKARYOTE_SUBTILIS_SIGMAA: ClassVar[Self]
    RNAP_PROKARYOTE_SUBTILIS_SIGMAB: ClassVar[Self]
    RNAP_PROKARYOTE_SYNECHOCYSTIS: ClassVar[Self]
    RNAP_PROKARYOTE_VHARVEYI_SIGMA54: ClassVar[Self]
    RNA_RIBOSWITCH: ClassVar[Self]
    RNA_RIBOZYME: ClassVar[Self]
    T3: ClassVar[Self]
    T3_T2: ClassVar[Self]
    T3_T4: ClassVar[Self]
    TERMINATOR: ClassVar[Self]
    TERMINATOR_DOUBLE: ClassVar[Self]
    TERMINATOR_SINGLE: ClassVar[Self]
    TRANSCRIPTIONAL: ClassVar[Self]
    VIRAL_VECTORS: ClassVar[Self]
    VIRAL_VECTORS_AAV: ClassVar[Self]
    VIRAL_VECTORS_AAV_CAPSID_CODING: ClassVar[Self]
    VIRAL_VECTORS_AAV_MISCELLANEOUS: ClassVar[Self]
    VIRAL_VECTORS_AAV_VECTOR_PLASMID: ClassVar[Self]


Category.BINDING_CELLULOSE = Category(
    uuid=UUID("aa3928df-9e74-4d13-9b5d-5178d7f8dbd4"),
    label="//binding/cellulose",
)
Category.BINDING_METAL = Category(
    uuid=UUID("4cfb1d25-f9bd-4fbb-8b90-64ab9ad0381d"),
    label="//binding/metal",
)
Category.BIOSAFETY = Category(
    uuid=UUID("e8e484f3-fab8-451b-b770-480690366853"),
    label="//biosafety",
)
Category.BIOSAFETY_KILL_SWITCH = Category(
    uuid=UUID("1f80037e-36a3-42ca-b439-7085bf45e3c9"),
    label="//biosafety/kill_switch",
)
Category.BIOSAFETY_SEMANTIC_CONTAINMENT = Category(
    uuid=UUID("7f798c72-0f5d-4afa-86ed-c61211582432"),
    label="//biosafety/semantic_containment",
)
Category.BIOSAFETY_XNASE = Category(
    uuid=UUID("7c38d50d-7f2b-4a97-8fcb-bc9e9839a950"),
    label="//biosafety/xnase",
)
Category.CDS = Category(
    uuid=UUID("3986f931-2d15-4dbd-a69d-45220b3c6de4"),
    label="//cds",
)
Category.CDS_BIOSYNTHESIS = Category(
    uuid=UUID("1c600327-d0cc-4032-b57e-51b75647006e"),
    label="//cds/biosynthesis",
)
Category.CDS_BIOSYNTHESIS_ANTHOCYANINS = Category(
    uuid=UUID("b36b3278-9be5-46d2-8225-6f39b1ef0cb4"),
    label="//cds/biosynthesis/anthocyanins",
)
Category.CDS_CHROMATINREMODELING = Category(
    uuid=UUID("7c8fa554-4d85-418a-a9cf-8681f53841c7"),
    label="//cds/chromatinremodeling",
)
Category.CDS_ENZYME = Category(
    uuid=UUID("162a0f8b-8ef2-409b-a17b-9bf5469fa64d"),
    label="//cds/enzyme",
)
Category.CDS_ENZYME_CHROMATINREMODELING = Category(
    uuid=UUID("04029e44-5636-40e1-a42d-91d773ac17ba"),
    label="//cds/enzyme/chromatinremodeling",
)
Category.CDS_ENZYME_DNAPOLYMERASE = Category(
    uuid=UUID("e8019d52-921f-4e16-b417-42c6aa89361f"),
    label="//cds/enzyme/dnapolymerase",
)
Category.CDS_ENZYME_DNASE = Category(
    uuid=UUID("9bfbf69e-7253-41a4-8f99-2321c6d05ea2"),
    label="//cds/enzyme/dnase",
)
Category.CDS_ENZYME_ENDONUCLEASE = Category(
    uuid=UUID("24eb8192-0eb6-45d1-8975-e0018e309ad7"),
    label="//cds/enzyme/endonuclease",
)
Category.CDS_ENZYME_ENDONUCLEASE_RESTRICTION = Category(
    uuid=UUID("8fb2719f-b207-4bbc-8859-754b592ce2ce"),
    label="//cds/enzyme/endonuclease/restriction",
)
Category.CDS_ENZYME_EXONUCLEASE = Category(
    uuid=UUID("49f5b4a0-1fd0-47ae-bfcb-6297423f0ba3"),
    label="//cds/enzyme/exonuclease",
)
Category.CDS_ENZYME_LIGASE = Category(
    uuid=UUID("f88a0586-04ce-4ea8-931a-f30124642847"),
    label="//cds/enzyme/ligase",
)
Category.CDS_ENZYME_LYSIS = Category(
    uuid=UUID("1702fd66-f370-4592-a884-3d4f0b59fbe9"),
    label="//cds/enzyme/lysis",
)
Category.CDS_ENZYME_METHYLATION = Category(
    uuid=UUID("27d20806-3f88-451a-ab52-37b72d6cd3b8"),
    label="//cds/enzyme/methylation",
)
Category.CDS_ENZYME_PHOSPHORYLATION = Category(
    uuid=UUID("1a0c9a3c-e647-4f43-afce-4d225556f284"),
    label="//cds/enzyme/phosphorylation",
)
Category.CDS_ENZYME_PROTEASE = Category(
    uuid=UUID("3c04b288-fd06-4aa4-bf18-e0e8f7e8ff51"),
    label="//cds/enzyme/protease",
)
Category.CDS_ENZYME_RNAP = Category(
    uuid=UUID("bab8a833-8129-4c88-b266-5394423c371f"),
    label="//cds/enzyme/rnap",
)
Category.CDS_ENZYME_RNAPOLYMERASE = Category(
    uuid=UUID("432bcdde-c3b4-4d39-ae29-3fca88a0ff43"),
    label="//cds/enzyme/rnapolymerase",
)
Category.CDS_LIGAND = Category(
    uuid=UUID("25ce8b0c-fe03-4051-b4da-5a446dd169b3"),
    label="//cds/ligand",
)
Category.CDS_LYSIS = Category(
    uuid=UUID("d2669554-9f37-4e86-bd01-b568a21a4ee3"),
    label="//cds/lysis",
)
Category.CDS_MEMBRANE = Category(
    uuid=UUID("96eec1f5-369f-4895-9d83-9607bd822d95"),
    label="//cds/membrane",
)
Category.CDS_MEMBRANE_CHANNEL = Category(
    uuid=UUID("4fae2ad0-ad15-46af-a332-3e67d0f264e3"),
    label="//cds/membrane/channel",
)
Category.CDS_MEMBRANE_EXTRACELLULAR = Category(
    uuid=UUID("3fbc2e32-095a-4833-bcef-219beaf79df6"),
    label="//cds/membrane/extracellular",
)
Category.CDS_MEMBRANE_LYSIS = Category(
    uuid=UUID("2b8558ba-d1e1-446b-a470-fc6206242a90"),
    label="//cds/membrane/lysis",
)
Category.CDS_MEMBRANE_PUMP = Category(
    uuid=UUID("8fc7862b-d5a0-4f8a-b7a6-136672ef3442"),
    label="//cds/membrane/pump",
)
Category.CDS_MEMBRANE_RECEPTOR = Category(
    uuid=UUID("15661704-deb0-46a3-b41d-5fd8126d8775"),
    label="//cds/membrane/receptor",
)
Category.CDS_MEMBRANE_TRANSPORTER = Category(
    uuid=UUID("ff6211f8-e185-46d7-ba89-38e301cff5c5"),
    label="//cds/membrane/transporter",
)
Category.CDS_RECEPTOR = Category(
    uuid=UUID("ae28f394-71d7-4f5f-a24c-9a01458987f8"),
    label="//cds/receptor",
)
Category.CDS_RECEPTOR_ANTIBODY = Category(
    uuid=UUID("291b22b5-1e8a-453c-85b4-ba8c7d781198"),
    label="//cds/receptor/antibody",
)
Category.CDS_REPORTER = Category(
    uuid=UUID("7387a14d-2203-48c0-a186-2505486abf3a"),
    label="//cds/reporter",
)
Category.CDS_REPORTER_CFP = Category(
    uuid=UUID("5cc3b818-7c8b-4a41-a031-1c46ac14a24d"),
    label="//cds/reporter/cfp",
)
Category.CDS_REPORTER_CHROMOPROTEIN = Category(
    uuid=UUID("8c4f8fc6-3583-4561-a69f-03f2b030b599"),
    label="//cds/reporter/chromoprotein",
)
Category.CDS_REPORTER_GFP = Category(
    uuid=UUID("30b16a3c-acf1-4d3c-a91c-88a1236911e8"),
    label="//cds/reporter/gfp",
)
Category.CDS_REPORTER_RFP = Category(
    uuid=UUID("0466cd6c-adbb-4f7e-a538-c4ee4ffda0fe"),
    label="//cds/reporter/rfp",
)
Category.CDS_REPORTER_YFP = Category(
    uuid=UUID("2ab286ad-0720-4cd2-921e-0304ba16c634"),
    label="//cds/reporter/yfp",
)
Category.CDS_SELECTIONMARKER = Category(
    uuid=UUID("abdbeb5b-0ca3-4780-ada4-2798a6edd85d"),
    label="//cds/selectionmarker",
)
Category.CDS_SELECTIONMARKER_ANTIBIOTICRESISTANCE = Category(
    uuid=UUID("1f5775ad-6597-4197-809b-e83e143d0871"),
    label="//cds/selectionmarker/antibioticresistance",
)
Category.CDS_TRANSCRIPTIONALREGULATOR = Category(
    uuid=UUID("27eb99eb-939a-45b4-ab21-79659d4f7c5b"),
    label="//cds/transcriptionalregulator",
)
Category.CDS_TRANSCRIPTIONALREGULATOR_ACTIVATOR = Category(
    uuid=UUID("13043ba5-6fda-47b7-89ef-6d7aed146afb"),
    label="//cds/transcriptionalregulator/activator",
)
Category.CDS_TRANSCRIPTIONALREGULATOR_REPRESSOR = Category(
    uuid=UUID("df7e88bd-1db1-4529-84a8-c529c365dab2"),
    label="//cds/transcriptionalregulator/repressor",
)
Category.CHASSIS = Category(
    uuid=UUID("b3c20f6d-0195-4612-b72c-9362a442ad00"),
    label="//chassis",
)
Category.CHASSIS_AFERROOXIDANS = Category(
    uuid=UUID("ba79b112-3543-4e4a-8d05-2c8918b786ea"),
    label="//chassis/aferrooxidans",
)
Category.CHASSIS_BACTERIOPHAGE = Category(
    uuid=UUID("55c7a1eb-ff2b-4990-ad52-b5eede9b352a"),
    label="//chassis/bacteriophage",
)
Category.CHASSIS_BACTERIOPHAGE_T3 = Category(
    uuid=UUID("44a91823-d52c-4f67-a927-cc9715027772"),
    label="//chassis/bacteriophage/t3",
)
Category.CHASSIS_BACTERIOPHAGE_T4 = Category(
    uuid=UUID("eac6a5a6-2870-462a-a18c-26c7f9692465"),
    label="//chassis/bacteriophage/t4",
)
Category.CHASSIS_BACTERIOPHAGE_T7 = Category(
    uuid=UUID("91b9ba13-c39a-46bb-b51b-bdd01df279b5"),
    label="//chassis/bacteriophage/t7",
)
Category.CHASSIS_EUKARYOTE = Category(
    uuid=UUID("6a92dbed-ffc9-47d3-af40-730c76409f6a"),
    label="//chassis/eukaryote",
)
Category.CHASSIS_EUKARYOTE_ATHALIANA = Category(
    uuid=UUID("78553a3c-2106-4c87-8ac5-cfda850c5dcc"),
    label="//chassis/eukaryote/athaliana",
)
Category.CHASSIS_EUKARYOTE_HUMAN = Category(
    uuid=UUID("94ac85be-af61-4f30-86b2-6d218e4dd75a"),
    label="//chassis/eukaryote/human",
)
Category.CHASSIS_EUKARYOTE_MPOLYMORPHA = Category(
    uuid=UUID("383330d9-4ae7-4d9c-b0f3-492bdbe4a4fe"),
    label="//chassis/eukaryote/mpolymorpha",
)
Category.CHASSIS_EUKARYOTE_NBENTHAMIANA = Category(
    uuid=UUID("edbf991c-a353-4ca9-b617-11d8cf3d3650"),
    label="//chassis/eukaryote/nbenthamiana",
)
Category.CHASSIS_EUKARYOTE_NTABACUM = Category(
    uuid=UUID("66019ba6-fee5-422c-8568-da38eefb1225"),
    label="//chassis/eukaryote/ntabacum",
)
Category.CHASSIS_EUKARYOTE_PICHIA = Category(
    uuid=UUID("44df4447-be79-464b-bbc9-7237fece2489"),
    label="//chassis/eukaryote/pichia",
)
Category.CHASSIS_EUKARYOTE_PLANTS_OTHER = Category(
    uuid=UUID("28c170f4-3423-460b-bfde-8bc4968c6a70"),
    label="//chassis/eukaryote/plants/other",
)
Category.CHASSIS_EUKARYOTE_PPATENS = Category(
    uuid=UUID("c288d192-119b-4696-8027-bf5024b0e4f0"),
    label="//chassis/eukaryote/ppatens",
)
Category.CHASSIS_EUKARYOTE_YEAST = Category(
    uuid=UUID("75af71c5-7998-41a7-b4eb-8f6f586f7fa7"),
    label="//chassis/eukaryote/yeast",
)
Category.CHASSIS_MISCELLANEOUS = Category(
    uuid=UUID("94c0e3be-e692-4b2f-b3a8-9b1418691a9e"),
    label="//chassis/miscellaneous",
)
Category.CHASSIS_MULTIHOST = Category(
    uuid=UUID("60365444-c2e6-4892-b6f5-3f6d47dd7ec9"),
    label="//chassis/multihost",
)
Category.CHASSIS_ORGANELLE = Category(
    uuid=UUID("d380b0d9-e24a-4669-bbf7-054c7b2103e9"),
    label="//chassis/organelle",
)
Category.CHASSIS_ORGANELLE_CHLOROPLAST = Category(
    uuid=UUID("61dbd5a4-9575-4d41-bec1-2a2d2972380d"),
    label="//chassis/organelle/chloroplast",
)
Category.CHASSIS_ORGANELLE_MITOCHONDRION = Category(
    uuid=UUID("1d2c2925-1061-486b-87cb-acd90e91279b"),
    label="//chassis/organelle/mitochondrion",
)
Category.CHASSIS_PROKARYOTE = Category(
    uuid=UUID("4d56e7a4-6be9-4e4b-80c6-d6a3539b0e2f"),
    label="//chassis/prokaryote",
)
Category.CHASSIS_PROKARYOTE_BCEPACIA = Category(
    uuid=UUID("9749e62f-9608-4b1d-b71f-725c85bad202"),
    label="//chassis/prokaryote/bcepacia",
)
Category.CHASSIS_PROKARYOTE_BSUBTILIS = Category(
    uuid=UUID("60f92897-aa59-4c44-9c9b-01a480229ffd"),
    label="//chassis/prokaryote/bsubtilis",
)
Category.CHASSIS_PROKARYOTE_CYANOBACTERIUM = Category(
    uuid=UUID("80a38480-4be6-4f9b-98d5-8d4247e59de5"),
    label="//chassis/prokaryote/cyanobacterium",
)
Category.CHASSIS_PROKARYOTE_ECOLI = Category(
    uuid=UUID("2b82773d-06be-4e16-980f-f5dd5a0705aa"),
    label="//chassis/prokaryote/ecoli",
)
Category.CHASSIS_PROKARYOTE_ECOLI_NISSLE = Category(
    uuid=UUID("6e951d54-6405-438a-a5f2-10813608d0d6"),
    label="//chassis/prokaryote/ecoli/nissle",
)
Category.CHASSIS_PROKARYOTE_GXYLINUS = Category(
    uuid=UUID("8a378de1-d70e-45fc-b5b9-48a87f31ebab"),
    label="//chassis/prokaryote/gxylinus",
)
Category.CHASSIS_PROKARYOTE_LACTOBACILLUS = Category(
    uuid=UUID("a1529ba5-795a-4d6d-9eb8-3dd5d8d83982"),
    label="//chassis/prokaryote/lactobacillus",
)
Category.CHASSIS_PROKARYOTE_LACTOCOCCUS = Category(
    uuid=UUID("91a3d905-eb8d-4456-9899-24dff0493d45"),
    label="//chassis/prokaryote/lactococcus",
)
Category.CHASSIS_PROKARYOTE_MFLORUM = Category(
    uuid=UUID("f9400685-60fc-4f82-902b-1a17b755512c"),
    label="//chassis/prokaryote/mflorum",
)
Category.CHASSIS_PROKARYOTE_PANANATIS = Category(
    uuid=UUID("1939f5a1-380d-4049-92c5-9b64714f4309"),
    label="//chassis/prokaryote/pananatis",
)
Category.CHASSIS_PROKARYOTE_PMIRABILIS = Category(
    uuid=UUID("f1636cd8-d441-496f-a91b-2a5b9f441034"),
    label="//chassis/prokaryote/pmirabilis",
)
Category.CHASSIS_PROKARYOTE_PPUTIDA = Category(
    uuid=UUID("72913233-41d1-43fd-8705-7ffd4e727e99"),
    label="//chassis/prokaryote/pputida",
)
Category.CHASSIS_PROKARYOTE_REUPHORA = Category(
    uuid=UUID("9bd75ff2-27c5-4ef3-b8d8-7c2138a6ad19"),
    label="//chassis/prokaryote/reuphora",
)
Category.CHASSIS_PROKARYOTE_RRADIOBACTER = Category(
    uuid=UUID("b1cfa1e4-9c74-40fe-a5fa-949982b122eb"),
    label="//chassis/prokaryote/rradiobacter",
)
Category.CHASSIS_PROKARYOTE_SALMONELLA = Category(
    uuid=UUID("fc21040c-0ff1-4c13-96d7-5f0a7608eeff"),
    label="//chassis/prokaryote/salmonella",
)
Category.CHASSIS_PROKARYOTE_SESPANAENSIS = Category(
    uuid=UUID("d9c17349-578c-4efb-89ad-af3fef4fdf51"),
    label="//chassis/prokaryote/sespanaensis",
)
Category.CHASSIS_PROKARYOTE_SUBTILIS = Category(
    uuid=UUID("65625e21-c584-4f90-8190-c7ff8c113d1d"),
    label="//chassis/prokaryote/subtilis",
)
Category.CHASSIS_PROKARYOTE_SYNECHOCYSTIS = Category(
    uuid=UUID("f87d8241-183f-4e93-ac30-cfac829022c6"),
    label="//chassis/prokaryote/synechocystis",
)
Category.CHASSIS_PROKARYOTE_VHARVEYI = Category(
    uuid=UUID("ea01c9aa-4369-4f97-bf20-78ee383422b5"),
    label="//chassis/prokaryote/vharveyi",
)
Category.CLASSIC_COMPOSITE_UNCATEGORIZED = Category(
    uuid=UUID("df474a70-cca2-4da6-bd9c-d2f2bc66b669"),
    label="//classic/composite/uncategorized",
)
Category.CLASSIC_DEVICE_UNCATEGORIZED = Category(
    uuid=UUID("4453eed2-eb52-4b92-b670-b2a33b5b1f58"),
    label="//classic/device/uncategorized",
)
Category.CLASSIC_GENERATOR_PLASMIDS = Category(
    uuid=UUID("46dd3a2d-2a9e-4fdd-9c73-f6e44381d215"),
    label="//classic/generator/plasmids",
)
Category.CLASSIC_GENERATOR_PRC = Category(
    uuid=UUID("bd0f6042-76a8-4dd5-bbce-1a1c0b6ddfe2"),
    label="//classic/generator/prc",
)
Category.CLASSIC_GENERATOR_PRCT = Category(
    uuid=UUID("6b98d80d-1501-4544-b05d-c8d9a7ab6be3"),
    label="//classic/generator/prct",
)
Category.CLASSIC_GENERATOR_RC = Category(
    uuid=UUID("c79c16d3-67b0-4f2e-a1aa-a5c2f7b8f639"),
    label="//classic/generator/rc",
)
Category.CLASSIC_GENERATOR_RCT = Category(
    uuid=UUID("62c5a37d-aaa6-42ca-8feb-6aabb29c50c5"),
    label="//classic/generator/rct",
)
Category.CLASSIC_GENERATOR_UNCATEGORIZED = Category(
    uuid=UUID("0d2d6e98-4122-44ce-847c-c444a5063952"),
    label="//classic/generator/uncategorized",
)
Category.CLASSIC_INTERMEDIATE_UNCATEGORIZED = Category(
    uuid=UUID("7fb45f74-d6e8-40fd-bab0-64ff2d9fca97"),
    label="//classic/intermediate/uncategorized",
)
Category.CLASSIC_INVERTER_UNCATEGORIZED = Category(
    uuid=UUID("8e01f77f-734c-44c4-a915-88c3fc697d72"),
    label="//classic/inverter/uncategorized",
)
Category.CLASSIC_MEASUREMENT_O_H = Category(
    uuid=UUID("89ccf4b6-605e-4c16-8baf-3c189fe88dac"),
    label="//classic/measurement/o_h",
)
Category.CLASSIC_MEASUREMENT_UNCATEGORIZED = Category(
    uuid=UUID("0d513911-abe5-4047-8443-7ba8783d95f9"),
    label="//classic/measurement/uncategorized",
)
Category.CLASSIC_OTHER_UNCATEGORIZED = Category(
    uuid=UUID("7b42b9cf-fcd2-49ed-b648-c257fb2304db"),
    label="//classic/other/uncategorized",
)
Category.CLASSIC_PLASMID_MEASUREMENT = Category(
    uuid=UUID("d8bc6cfe-cb7b-4fea-b7f1-5ae00a690d25"),
    label="//classic/plasmid/measurement",
)
Category.CLASSIC_PLASMID_UNCATEGORIZED = Category(
    uuid=UUID("1a59149d-1b56-4582-9c42-0e43598d702a"),
    label="//classic/plasmid/uncategorized",
)
Category.CLASSIC_PROJECT_UNCATEGORIZED = Category(
    uuid=UUID("5ef59e54-3b90-4046-8d9f-acfb2a4ddcf6"),
    label="//classic/project/uncategorized",
)
Category.CLASSIC_RBS_UNCATEGORIZED = Category(
    uuid=UUID("ee28e1e1-a035-4d27-a308-4374ce00bca2"),
    label="//classic/rbs/uncategorized",
)
Category.CLASSIC_REGULATORY_OTHER = Category(
    uuid=UUID("1ae149fd-688d-4a8e-af0c-bf8539742220"),
    label="//classic/regulatory/other",
)
Category.CLASSIC_REGULATORY_UNCATEGORIZED = Category(
    uuid=UUID("f2ba7af9-b4a0-4b32-be47-47d731d598a8"),
    label="//classic/regulatory/uncategorized",
)
Category.CLASSIC_REPORTER = Category(
    uuid=UUID("0c46589c-47e8-46df-aa0f-1ddb1e94de15"),
    label="//classic/reporter",
)
Category.CLASSIC_REPORTER_CONSTITUTIVE = Category(
    uuid=UUID("f259cf50-fc1b-4c4c-a7a9-87b6abba1ba4"),
    label="//classic/reporter/constitutive",
)
Category.CLASSIC_REPORTER_MULTIPLE = Category(
    uuid=UUID("6ab46971-885f-4462-b28a-f403250ac980"),
    label="//classic/reporter/multiple",
)
Category.CLASSIC_REPORTER_PRET = Category(
    uuid=UUID("00e6bf15-3ba6-4a82-90cc-4aec8ba11b63"),
    label="//classic/reporter/pret",
)
Category.CLASSIC_REPORTER_RET = Category(
    uuid=UUID("b2e36d90-09a9-4adf-82ce-b1a4434ff1d8"),
    label="//classic/reporter/ret",
)
Category.CLASSIC_RNA_UNCATEGORIZED = Category(
    uuid=UUID("8a293c89-55f3-4292-a5e9-1237a8ebd85f"),
    label="//classic/rna/uncategorized",
)
Category.CLASSIC_SIGNALLING_RECEIVER = Category(
    uuid=UUID("8328b0e9-3c58-429a-9b47-d2d1a365e3cd"),
    label="//classic/signalling/receiver",
)
Category.CLASSIC_SIGNALLING_SENDER = Category(
    uuid=UUID("bfa0edaf-7fee-480f-b0c9-06e724a3bb4a"),
    label="//classic/signalling/sender",
)
Category.CLASSIC_TEMPORARY_UNCATEGORIZED = Category(
    uuid=UUID("ca8f99f6-1b16-412f-9a69-f835b160403b"),
    label="//classic/temporary/uncategorized",
)
Category.DIRECTION = Category(
    uuid=UUID("1f5bc8ed-5ea7-4636-86fb-5929002387ab"),
    label="//direction",
)
Category.DIRECTION_BIDIRECTIONAL = Category(
    uuid=UUID("ee4d2f4d-d5a7-4d4c-9b42-4fa9fc113d7b"),
    label="//direction/bidirectional",
)
Category.DIRECTION_FORWARD = Category(
    uuid=UUID("d56b812e-7f4d-4c8d-8a11-f16969d3012d"),
    label="//direction/forward",
)
Category.DIRECTION_REVERSE = Category(
    uuid=UUID("c1ddca89-c605-48d2-a9a5-1283ad065dfe"),
    label="//direction/reverse",
)
Category.DNA = Category(
    uuid=UUID("898f4ea1-03bc-4c10-b047-3c6b0abdbfef"),
    label="//dna",
)
Category.DNA_APTAMER = Category(
    uuid=UUID("494a9497-560e-493d-aba9-e114f6358045"),
    label="//dna/aptamer",
)
Category.DNA_BIOSCAFFOLD = Category(
    uuid=UUID("81a71e66-6498-4bd3-b533-5b3d396c4af2"),
    label="//dna/bioscaffold",
)
Category.DNA_CHROMOSOMALINTEGRATION = Category(
    uuid=UUID("bcf6c6e8-9a1d-46c9-9222-c0a685c84c07"),
    label="//dna/chromosomalintegration",
)
Category.DNA_CLONINGSITE = Category(
    uuid=UUID("396de333-c001-4c29-82fb-6eed9c01cadf"),
    label="//dna/cloningsite",
)
Category.DNA_CONJUGATION = Category(
    uuid=UUID("5c5e3e60-4249-48e3-9501-a32958731d8b"),
    label="//dna/conjugation",
)
Category.DNA_DNAZYME = Category(
    uuid=UUID("1ef604e0-e5ed-497f-87a6-5eac54341767"),
    label="//dna/dnazyme",
)
Category.DNA_NUCLEOTIDE = Category(
    uuid=UUID("6759026c-1a29-43da-aa19-7dae97786fc1"),
    label="//dna/nucleotide",
)
Category.DNA_ORIGAMI = Category(
    uuid=UUID("a0639d9e-6329-4d94-a1b2-0dc1c1e291b2"),
    label="//dna/origami",
)
Category.DNA_ORIGIN_OF_REPLICATION = Category(
    uuid=UUID("5f61a8fc-ac00-43f1-b45c-2cf204312701"),
    label="//dna/origin_of_replication",
)
Category.DNA_PRIMERBINDINGSITE = Category(
    uuid=UUID("7781992c-f95c-4e78-9fd0-96c5ae78b602"),
    label="//dna/primerbindingsite",
)
Category.DNA_RESTRICTIONSITE = Category(
    uuid=UUID("eaf2c615-124c-4802-b452-00a9dc8097e3"),
    label="//dna/restrictionsite",
)
Category.DNA_SCAR = Category(
    uuid=UUID("3a21a34e-b6b0-43a0-839a-c5b18c67ccf2"),
    label="//dna/scar",
)
Category.DNA_SPACER = Category(
    uuid=UUID("3d2a6948-01b7-41bf-92ab-ff7178827e38"),
    label="//dna/spacer",
)
Category.DNA_TRANSPOSOME_TN5 = Category(
    uuid=UUID("72703abb-6160-4cb3-93be-f71e404fda22"),
    label="//dna/transposome/tn5",
)
Category.DNA_TRANSPOSON = Category(
    uuid=UUID("3e2272a9-5769-42bd-9bba-c6ffecc60f87"),
    label="//dna/transposon",
)
Category.EXTREMOPHILES = Category(
    uuid=UUID("c48df00e-e3e7-4fa4-887a-14f29f54d024"),
    label="extremophiles",
)
Category.FUNCTION_BIOFUELS = Category(
    uuid=UUID("b29da7b0-6650-473d-97a1-acd6353b5b12"),
    label="//function/biofuels",
)
Category.FUNCTION_BIOSYNTHESIS = Category(
    uuid=UUID("9d54ca12-15cf-4cd2-87a8-f00b0fd135e8"),
    label="//function/biosynthesis",
)
Category.FUNCTION_BIOSYNTHESIS_AHL = Category(
    uuid=UUID("af926a34-04fb-4aee-8126-dfc94acbd915"),
    label="//function/biosynthesis/ahl",
)
Category.FUNCTION_BIOSYNTHESIS_BUTANOL = Category(
    uuid=UUID("2da0d462-41fa-4ce0-bc09-e398fd0063d5"),
    label="//function/biosynthesis/butanol",
)
Category.FUNCTION_BIOSYNTHESIS_CELLULOSE = Category(
    uuid=UUID("911e88ba-88f3-46de-a84d-bcf53e27c826"),
    label="//function/biosynthesis/cellulose",
)
Category.FUNCTION_BIOSYNTHESIS_HEME = Category(
    uuid=UUID("95db5475-e80b-4264-b185-a12e1bcdfdef"),
    label="//function/biosynthesis/heme",
)
Category.FUNCTION_BIOSYNTHESIS_ISOPRENOID = Category(
    uuid=UUID("0dd1a49a-c1e9-45fa-9fa3-63f59c8dddfc"),
    label="//function/biosynthesis/isoprenoid",
)
Category.FUNCTION_BIOSYNTHESIS_ODORANT = Category(
    uuid=UUID("e97aa8cb-b7e0-48a9-aacd-f28666f98fd0"),
    label="//function/biosynthesis/odorant",
)
Category.FUNCTION_BIOSYNTHESIS_PHYCOCYANOBILIN = Category(
    uuid=UUID("a38a52c2-8b26-44e9-81c6-9ecc8660f79b"),
    label="//function/biosynthesis/phycocyanobilin",
)
Category.FUNCTION_BIOSYNTHESIS_PLASTIC = Category(
    uuid=UUID("7fdb9201-5e15-4c0e-a306-b67e46168dc9"),
    label="//function/biosynthesis/plastic",
)
Category.FUNCTION_BIOSYNTHESIS_PYOCYANIN = Category(
    uuid=UUID("632cd3e5-0037-432e-811d-e2ab7783e532"),
    label="//function/biosynthesis/pyocyanin",
)
Category.FUNCTION_CELLDEATH = Category(
    uuid=UUID("b2835ba5-9828-440c-9e4a-7b26d613b31d"),
    label="//function/celldeath",
)
Category.FUNCTION_CELLSIGNALLING = Category(
    uuid=UUID("a1173514-c86f-499e-abb3-0d18330e0f0c"),
    label="//function/cellsignalling",
)
Category.FUNCTION_COLIROID = Category(
    uuid=UUID("a5020564-0c58-40c3-a235-cf00b6edef57"),
    label="//function/coliroid",
)
Category.FUNCTION_CONJUGATION = Category(
    uuid=UUID("ba085e9f-2bbe-4e39-94e9-ee0e5ec4732f"),
    label="//function/conjugation",
)
Category.FUNCTION_CRISPR = Category(
    uuid=UUID("7fa7e6f9-3474-4b87-9d49-c6c2d5d7deda"),
    label="//function/crispr",
)
Category.FUNCTION_CRISPR_CAS = Category(
    uuid=UUID("1e127f07-f90f-4d2a-af19-cb9506cd83d5"),
    label="//function/crispr/cas",
)
Category.FUNCTION_CRISPR_CAS9 = Category(
    uuid=UUID("03434acf-3604-46e5-83f4-a4eda7d946db"),
    label="//function/crispr/cas9",
)
Category.FUNCTION_CRISPR_GRNA = Category(
    uuid=UUID("5a1a8765-7820-470f-83a7-45c66b63dd49"),
    label="//function/crispr/grna",
)
Category.FUNCTION_CRISPR_GRNA_CONSTRUCT = Category(
    uuid=UUID("4b20740f-addb-450c-b76e-de28f2c9c760"),
    label="//function/crispr/grna/construct",
)
Category.FUNCTION_CRISPR_GRNA_EFFICIENT = Category(
    uuid=UUID("23888a75-afc2-40a4-b0aa-ab5955610540"),
    label="//function/crispr/grna/efficient",
)
Category.FUNCTION_CRISPR_GRNA_REPEAT = Category(
    uuid=UUID("82f83cb2-eab8-4846-bf2b-85706608c8ea"),
    label="//function/crispr/grna/repeat",
)
Category.FUNCTION_CRISPR_GRNA_SPACER = Category(
    uuid=UUID("68f3824f-be34-4fc8-80b8-276aa7043dc7"),
    label="//function/crispr/grna/spacer",
)
Category.FUNCTION_DEGRADATION = Category(
    uuid=UUID("0ce28e2a-2075-493c-a912-48841dacdf14"),
    label="//function/degradation",
)
Category.FUNCTION_DEGRADATION_AHL = Category(
    uuid=UUID("3b15279c-603c-4251-a6e2-f796279b0c04"),
    label="//function/degradation/ahl",
)
Category.FUNCTION_DEGRADATION_BISPHENOL = Category(
    uuid=UUID("7c7e8134-7f00-4759-a0e2-81e4e7d232ac"),
    label="//function/degradation/bisphenol",
)
Category.FUNCTION_DEGRADATION_CELLULOSE = Category(
    uuid=UUID("30794bb4-504d-481f-8bef-645f8bba2920"),
    label="//function/degradation/cellulose",
)
Category.FUNCTION_DNA = Category(
    uuid=UUID("10327cac-2f64-449b-9dfc-950ad833ec8a"),
    label="//function/dna",
)
Category.FUNCTION_FRET = Category(
    uuid=UUID("a86fa241-6a4d-4213-a93a-b8fe39d24ba6"),
    label="//function/fret",
)
Category.FUNCTION_IMMUNOLOGY = Category(
    uuid=UUID("a2b7a0d6-e271-4f11-bebb-b14d4fce649b"),
    label="//function/immunology",
)
Category.FUNCTION_MISMATCHREPAIR = Category(
    uuid=UUID("956eab31-6f07-41a1-8ac1-5495996891b8"),
    label="//function/mismatchrepair",
)
Category.FUNCTION_MOTILITY = Category(
    uuid=UUID("009cdad3-7680-4aa2-91c3-4f2456dea62e"),
    label="//function/motility",
)
Category.FUNCTION_ODOR = Category(
    uuid=UUID("c1bab10e-f9e5-4861-9d78-8f4dd8a78269"),
    label="//function/odor",
)
Category.FUNCTION_RECOMBINATION = Category(
    uuid=UUID("af8cc7d3-64a7-42d1-a524-f6a76ddfdee7"),
    label="//function/recombination",
)
Category.FUNCTION_RECOMBINATION_CRE = Category(
    uuid=UUID("3f31c438-1bd1-4917-9752-3b54969478c3"),
    label="//function/recombination/cre",
)
Category.FUNCTION_RECOMBINATION_FIM = Category(
    uuid=UUID("3185513a-ecb6-4c9b-9092-d98d3ee2d872"),
    label="//function/recombination/fim",
)
Category.FUNCTION_RECOMBINATION_FLP = Category(
    uuid=UUID("60aae11b-9139-4b37-a652-33b56b9d4e71"),
    label="//function/recombination/flp",
)
Category.FUNCTION_RECOMBINATION_HIN = Category(
    uuid=UUID("a562772d-2d93-4818-a4ef-310615a61159"),
    label="//function/recombination/hin",
)
Category.FUNCTION_RECOMBINATION_LAMBDA = Category(
    uuid=UUID("5775198f-83b8-4f48-b02f-0650c451654d"),
    label="//function/recombination/lambda",
)
Category.FUNCTION_RECOMBINATION_P22 = Category(
    uuid=UUID("923253c3-48fd-479f-aca9-1fa7a5e03416"),
    label="//function/recombination/p22",
)
Category.FUNCTION_RECOMBINATION_XER = Category(
    uuid=UUID("c71567dd-6347-4830-b1eb-f50760ce3b80"),
    label="//function/recombination/xer",
)
Category.FUNCTION_REGULATION_TRANSCRIPTIONAL = Category(
    uuid=UUID("90def41d-fc5e-4763-aa7c-d7e5e0b56f2c"),
    label="//function/regulation/transcriptional",
)
Category.FUNCTION_REPORTER = Category(
    uuid=UUID("dcd1b823-3023-4d40-8185-7307e917e9d2"),
    label="//function/reporter",
)
Category.FUNCTION_REPORTER_COLOR = Category(
    uuid=UUID("cf00687b-c997-43db-91e2-bd89451e6a3c"),
    label="//function/reporter/color",
)
Category.FUNCTION_REPORTER_FLUORESCENCE = Category(
    uuid=UUID("0494c0bb-3396-42b4-8968-fc58565f20b1"),
    label="//function/reporter/fluorescence",
)
Category.FUNCTION_REPORTER_LIGHT = Category(
    uuid=UUID("9386de4f-b243-401d-bfba-e1c6b1c61100"),
    label="//function/reporter/light",
)
Category.FUNCTION_REPORTER_PIGMENT = Category(
    uuid=UUID("c07602c5-6d16-4932-a9c7-f7dd8ae36242"),
    label="//function/reporter/pigment",
)
Category.FUNCTION_SENSOR = Category(
    uuid=UUID("fd43e1af-4bd3-428c-a146-e329cb80af47"),
    label="//function/sensor",
)
Category.FUNCTION_SENSOR_LEAD = Category(
    uuid=UUID("fce07f54-2b62-4576-bdfd-431886447b9e"),
    label="//function/sensor/lead",
)
Category.FUNCTION_SENSOR_LIGHT = Category(
    uuid=UUID("4b5c4b2c-b35c-4fea-993d-c4e64d2bbaf8"),
    label="//function/sensor/light",
)
Category.FUNCTION_SENSOR_METAL = Category(
    uuid=UUID("e494be2b-ec17-4ded-899b-9bb8ed8c6742"),
    label="//function/sensor/metal",
)
Category.FUNCTION_STRUCTURES = Category(
    uuid=UUID("932ac842-c2e4-4d7c-928b-d2853104dc72"),
    label="//function/structures",
)
Category.FUNCTION_TUMORKILLINGBACTERIA = Category(
    uuid=UUID("a60fb942-14c3-4212-a692-cb8f5d74f16a"),
    label="//function/tumorkillingbacteria",
)
Category.PLASMID = Category(
    uuid=UUID("6691747c-0d0e-4395-8c86-dd86873dba46"),
    label="//plasmid",
)
Category.PLASMIDBACKBONE = Category(
    uuid=UUID("02863b5f-ddfb-4072-a99d-13d2a09a156d"),
    label="//plasmidbackbone",
)
Category.PLASMIDBACKBONE_ARCHIVE = Category(
    uuid=UUID("2ec58109-8632-45d4-bea5-e27b23e58663"),
    label="//plasmidbackbone/archive",
)
Category.PLASMIDBACKBONE_ASSEMBLY = Category(
    uuid=UUID("0f818ff8-f065-40e4-9e01-7a0900215061"),
    label="//plasmidbackbone/assembly",
)
Category.PLASMIDBACKBONE_ASSEMBLY_TYPEIIS = Category(
    uuid=UUID("e137adde-9295-462b-841e-12ab2e528240"),
    label="//plasmidbackbone/assembly/typeiis",
)
Category.PLASMIDBACKBONE_COMPONENT_DEFAULTINSERT = Category(
    uuid=UUID("a66e8c0e-0180-4371-97fb-4f67e8b5d8d1"),
    label="//plasmidbackbone/component/defaultinsert",
)
Category.PLASMIDBACKBONE_COMPONENT_SELECTIONMARKER_ANTIBIOTICRESISTANCE = Category(  # noqa: E501
    uuid=UUID("dfe709d9-2ba6-4eaa-b3d3-5abc41a23fc1"),
    label="//plasmidbackbone/component/selectionmarker/antibioticresistance",
)
Category.PLASMIDBACKBONE_COPYNUMBER = Category(
    uuid=UUID("103bb967-fb8d-4cf8-bfa4-5f6fc9fc1573"),
    label="//plasmidbackbone/copynumber",
)
Category.PLASMIDBACKBONE_COPYNUMBER_HIGH = Category(
    uuid=UUID("0a7a75f7-5b05-440d-8504-aef315ac2392"),
    label="//plasmidbackbone/copynumber/high",
)
Category.PLASMIDBACKBONE_COPYNUMBER_INDUCIBLE = Category(
    uuid=UUID("b375daac-c46c-4b38-8e22-d4751bbc451e"),
    label="//plasmidbackbone/copynumber/inducible",
)
Category.PLASMIDBACKBONE_COPYNUMBER_LOW = Category(
    uuid=UUID("837bd789-fc3d-47e2-b8c5-92b997c8fd9d"),
    label="//plasmidbackbone/copynumber/low",
)
Category.PLASMIDBACKBONE_COPYNUMBER_MEDIUM = Category(
    uuid=UUID("5a3ce828-4a6e-4088-b005-e454446eb479"),
    label="//plasmidbackbone/copynumber/medium",
)
Category.PLASMIDBACKBONE_EXPRESSION = Category(
    uuid=UUID("d57d9211-8b6d-4cb2-b0d5-32d4279d0da9"),
    label="//plasmidbackbone/expression",
)
Category.PLASMIDBACKBONE_EXPRESSION_CONSTITUTIVE = Category(
    uuid=UUID("e35ff7c1-55c4-40ac-a67e-602a5c298dac"),
    label="//plasmidbackbone/expression/constitutive",
)
Category.PLASMIDBACKBONE_EXPRESSION_INDUCIBLE = Category(
    uuid=UUID("42e2c0d4-8f4a-46ca-9c51-84f3774254d0"),
    label="//plasmidbackbone/expression/inducible",
)
Category.PLASMIDBACKBONE_LIBRARYSCREENING = Category(
    uuid=UUID("1d93f26b-9bd7-45f3-8f19-11bfd4c5f8a0"),
    label="//plasmidbackbone/libraryscreening",
)
Category.PLASMIDBACKBONE_LIBRARYSCREENING_CODINGSEQUENCE = Category(
    uuid=UUID("1759216e-18a6-4cab-8ae6-dfd47e0d0379"),
    label="//plasmidbackbone/libraryscreening/codingsequence",
)
Category.PLASMIDBACKBONE_LIBRARYSCREENING_PROMOTER = Category(
    uuid=UUID("04693b92-2aba-4c66-bddd-b246a3653d88"),
    label="//plasmidbackbone/libraryscreening/promoter",
)
Category.PLASMIDBACKBONE_LIBRARYSCREENING_RBSCODINGSEQUENCE = Category(
    uuid=UUID("6128829f-a2b4-4479-96ff-0989582dd076"),
    label="//plasmidbackbone/libraryscreening/rbscodingsequence",
)
Category.PLASMIDBACKBONE_OPERATION = Category(
    uuid=UUID("e1458e75-4e74-4042-9b0e-7c2691aeb07d"),
    label="//plasmidbackbone/operation",
)
Category.PLASMIDBACKBONE_PROTEINFUSION = Category(
    uuid=UUID("01a9b05b-017c-43dc-a0a3-6ab9a9e3a976"),
    label="//plasmidbackbone/proteinfusion",
)
Category.PLASMIDBACKBONE_SYNTHESIS = Category(
    uuid=UUID("bc7f3f3d-7502-4673-b16b-42bb8fdcde8a"),
    label="//plasmidbackbone/synthesis",
)
Category.PLASMIDBACKBONE_VERSION_10 = Category(
    uuid=UUID("e7b2403b-09ba-41e3-b707-eb0e4d5d53ce"),
    label="//plasmidbackbone/version/10",
)
Category.PLASMIDBACKBONE_VERSION_3 = Category(
    uuid=UUID("43fc3b27-8989-4a98-934a-c84efa8bb92e"),
    label="//plasmidbackbone/version/3",
)
Category.PLASMIDBACKBONE_VERSION_4 = Category(
    uuid=UUID("3b53a06b-be93-40f3-93ff-0c902fc20f0b"),
    label="//plasmidbackbone/version/4",
)
Category.PLASMIDBACKBONE_VERSION_5 = Category(
    uuid=UUID("3fabe37a-ff2e-4887-a1de-9c981b79fe12"),
    label="//plasmidbackbone/version/5",
)
Category.PLASMID_CHROMOSOMALINTEGRATION = Category(
    uuid=UUID("c3b829e1-1ad8-441c-9201-c61052113ceb"),
    label="//plasmid/chromosomalintegration",
)
Category.PLASMID_COMPONENT_CLONINGSITE = Category(
    uuid=UUID("9a540825-505a-4c3e-87f0-cef53166eef5"),
    label="//plasmid/component/cloningsite",
)
Category.PLASMID_COMPONENT_INSULATION = Category(
    uuid=UUID("540eecaa-ee46-4172-add7-f953a04c715c"),
    label="//plasmid/component/insulation",
)
Category.PLASMID_COMPONENT_ORIGIN = Category(
    uuid=UUID("7b1d959b-d1c6-4c3f-835e-1efb2c4147f7"),
    label="//plasmid/component/origin",
)
Category.PLASMID_COMPONENT_OTHER = Category(
    uuid=UUID("9996dd3d-d208-4e0b-95ff-b684208c2863"),
    label="//plasmid/component/other",
)
Category.PLASMID_COMPONENT_PRIMERBINDINGSITE = Category(
    uuid=UUID("925f6ace-0023-45f3-ac49-491b47d2a16c"),
    label="//plasmid/component/primerbindingsite",
)
Category.PLASMID_CONSTRUCTION = Category(
    uuid=UUID("3aaf488b-00d6-42a4-815f-b0ed43f432e0"),
    label="//plasmid/construction",
)
Category.PLASMID_EXPRESSION = Category(
    uuid=UUID("3e6a1b0d-3f46-48f8-a38d-2f4f5cf0b130"),
    label="//plasmid/expression",
)
Category.PLASMID_EXPRESSION_T7 = Category(
    uuid=UUID("0b331794-eb96-43c8-bf0e-78043d15c306"),
    label="//plasmid/expression/t7",
)
Category.PLASMID_MEASUREMENT = Category(
    uuid=UUID("d619005e-f524-447a-923c-136989b13eac"),
    label="//plasmid/measurement",
)
Category.PLASMID_SP6 = Category(
    uuid=UUID("13f6ded3-6d02-45ff-bf3a-96b98e6f177c"),
    label="//plasmid/sp6",
)
Category.PRIMER_M13 = Category(
    uuid=UUID("4baa856d-90f0-441e-9dc4-f588cbfbac24"),
    label="//primer/m13",
)
Category.PRIMER_PART = Category(
    uuid=UUID("b923bac8-b8c1-4f08-b12f-d3836c03af4c"),
    label="//primer/part",
)
Category.PRIMER_PART_AMPLIFICATION = Category(
    uuid=UUID("5f16340c-ed0a-4813-9eeb-654443d70238"),
    label="//primer/part/amplification",
)
Category.PRIMER_PART_SEQUENCING = Category(
    uuid=UUID("c65d6d68-e818-45d0-a44e-416c0f1884b4"),
    label="//primer/part/sequencing",
)
Category.PRIMER_PLASMID_AMPLIFICATION = Category(
    uuid=UUID("a6344304-b820-4b03-9fbe-dca79531b8ed"),
    label="//primer/plasmid/amplification",
)
Category.PRIMER_REPORTER_CFP = Category(
    uuid=UUID("848fb1cc-c86f-4b6a-a520-77899f2ca183"),
    label="//primer/reporter/cfp",
)
Category.PRIMER_REPORTER_GFP = Category(
    uuid=UUID("2d6db6f3-c742-4ceb-ac1c-47e939035250"),
    label="//primer/reporter/gfp",
)
Category.PRIMER_REPORTER_YFP = Category(
    uuid=UUID("9146945d-e61d-4111-8758-ee1db80e82a9"),
    label="//primer/reporter/yfp",
)
Category.PRIMER_SP6 = Category(
    uuid=UUID("b23abf47-404e-413b-9927-b1d3eacefa4c"),
    label="//primer/sp6",
)
Category.PRIMER_T3 = Category(
    uuid=UUID("67d9d4c6-32e4-44e2-8e18-e004dd560389"),
    label="//primer/t3",
)
Category.PRIMER_T7 = Category(
    uuid=UUID("f289d81e-bcc5-47ed-88b2-245cb08e57a2"),
    label="//primer/t7",
)
Category.PROMOTER = Category(
    uuid=UUID("74858864-d348-4381-9df6-7c0714b646a3"),
    label="//promoter",
)
Category.PROMOTER_ANDERSON = Category(
    uuid=UUID("2ec1b2f2-46e0-4bf2-b2e9-908678d43413"),
    label="//promoter/anderson",
)
Category.PROMOTER_IRON = Category(
    uuid=UUID("14a6af6e-0efe-4b9d-848c-adb18ac43811"),
    label="//promoter/iron",
)
Category.PROMOTER_LOGIC_USTC = Category(
    uuid=UUID("d91259d9-f5cf-4cb0-a3dd-c54f6c70f373"),
    label="//promoter/logic/ustc",
)
Category.PROMOTER_STRESSKIT = Category(
    uuid=UUID("73651fcc-3cb2-4d7c-817a-0408be0a458a"),
    label="//promoter/stresskit",
)
Category.PROTEINDOMAIN = Category(
    uuid=UUID("7ec89a62-5673-4a52-8789-0a197cf60de4"),
    label="//proteindomain",
)
Category.PROTEINDOMAIN_ACTIVATION = Category(
    uuid=UUID("b468e396-3209-40dc-9a0f-500894213a23"),
    label="//proteindomain/activation",
)
Category.PROTEINDOMAIN_AFFINITY = Category(
    uuid=UUID("eb0fc973-daf9-4dee-85d2-59bdc5acafcd"),
    label="//proteindomain/affinity",
)
Category.PROTEINDOMAIN_BINDING = Category(
    uuid=UUID("cec29ad8-ccdb-4193-86ff-f389c665ec87"),
    label="//proteindomain/binding",
)
Category.PROTEINDOMAIN_BINDING_CELLULOSE = Category(
    uuid=UUID("c9a01861-5d00-41b2-b738-60300a2d93e3"),
    label="//proteindomain/binding/cellulose",
)
Category.PROTEINDOMAIN_CLEAVAGE = Category(
    uuid=UUID("406885c2-ee0f-4f85-bbe7-fe77c9cd86d5"),
    label="//proteindomain/cleavage",
)
Category.PROTEINDOMAIN_DEGRADATION = Category(
    uuid=UUID("47047241-7d65-48bf-a010-43a30aea207c"),
    label="//proteindomain/degradation",
)
Category.PROTEINDOMAIN_DNABINDING = Category(
    uuid=UUID("ad8851db-a098-4de2-ab15-b9d94e0818e3"),
    label="//proteindomain/dnabinding",
)
Category.PROTEINDOMAIN_HEAD = Category(
    uuid=UUID("e98a15b0-058d-4de9-9c7f-340696a1edcc"),
    label="//proteindomain/head",
)
Category.PROTEINDOMAIN_INTERNAL = Category(
    uuid=UUID("5339f995-fb79-4bd2-a62b-26d06ca965f1"),
    label="//proteindomain/internal",
)
Category.PROTEINDOMAIN_INTERNAL_SPECIAL = Category(
    uuid=UUID("57bac383-6e70-460d-8b1a-c096d11307e5"),
    label="//proteindomain/internal/special",
)
Category.PROTEINDOMAIN_LINKER = Category(
    uuid=UUID("43523273-6ff4-473e-93ac-f7dffe612fb4"),
    label="//proteindomain/linker",
)
Category.PROTEINDOMAIN_LOCALIZATION = Category(
    uuid=UUID("6e55dbb1-30ba-4c73-a01f-fc0a33cdd763"),
    label="//proteindomain/localization",
)
Category.PROTEINDOMAIN_REPRESSION = Category(
    uuid=UUID("a31b73a5-732a-4d9e-893c-9bfb723858f4"),
    label="//proteindomain/repression",
)
Category.PROTEINDOMAIN_TAIL = Category(
    uuid=UUID("e1ef6111-d34c-4c73-9b9d-bb048e81a0a1"),
    label="//proteindomain/tail",
)
Category.PROTEINDOMAIN_TRANSMEMBRANE = Category(
    uuid=UUID("1bec9c66-6d72-47fa-bf6a-e50b8da0b555"),
    label="//proteindomain/transmembrane",
)
Category.RBS_PROKARYOTE = Category(
    uuid=UUID("ad66d5e5-bcad-47ce-bd6d-e6a6d008928c"),
    label="//rbs/prokaryote",
)
Category.RBS_PROKARYOTE_CONSTITUTIVE = Category(
    uuid=UUID("b9514855-1ab3-4332-9499-d246eb63dcff"),
    label="//rbs/prokaryote/constitutive",
)
Category.RBS_PROKARYOTE_CONSTITUTIVE_ANDERSON = Category(
    uuid=UUID("5855071b-9438-489b-8f61-dd1e300ddef6"),
    label="//rbs/prokaryote/constitutive/anderson",
)
Category.RBS_PROKARYOTE_CONSTITUTIVE_COMMUNITY = Category(
    uuid=UUID("c714920e-3c28-4472-b7a2-d3252be37ea0"),
    label="//rbs/prokaryote/constitutive/community",
)
Category.RBS_PROKARYOTE_CONSTITUTIVE_CONSTITUTIVE = Category(
    uuid=UUID("fe028e6c-c455-49f7-bf3a-0a496e48555c"),
    label="//rbs/prokaryote/constitutive/constitutive",
)
Category.RBS_PROKARYOTE_CONSTITUTIVE_MISCELLANEOUS = Category(
    uuid=UUID("ae4be857-78cf-4ee9-95c1-0a26d930ea0c"),
    label="//rbs/prokaryote/constitutive/miscellaneous",
)
Category.RBS_PROKARYOTE_CONSTITUTIVE_RACKHAM = Category(
    uuid=UUID("e3cb3bdd-1e37-47c9-b7c8-c32cf32393a3"),
    label="//rbs/prokaryote/constitutive/rackham",
)
Category.RBS_PROKARYOTE_REGULATED_ISSACS = Category(
    uuid=UUID("561536ff-7648-460b-b3ea-aca52ee88407"),
    label="//rbs/prokaryote/regulated/issacs",
)
Category.RBS_PROKARYOTIC_CONSTITUTIVE_MISCELLANEOUS = Category(
    uuid=UUID("66b22b4a-3e8e-4ab5-9047-87380db55141"),
    label="//rbs/prokaryotic/constitutive/miscellaneous",
)
Category.RECEIVER = Category(
    uuid=UUID("68e5e8a6-75b6-4049-b7c0-da35b123df0e"),
    label="receiver",
)
Category.REGULATION = Category(
    uuid=UUID("a8eb122f-90ed-4b4f-82dd-5f11d2da280f"),
    label="//regulation",
)
Category.REGULATION_CONSTITUTIVE = Category(
    uuid=UUID("8d4683d1-2310-4a90-b875-bb1f354f7c05"),
    label="//regulation/constitutive",
)
Category.REGULATION_MULTIPLE = Category(
    uuid=UUID("8db04e5e-1ad3-4350-99f2-6b74edb8fdbb"),
    label="//regulation/multiple",
)
Category.REGULATION_NEGATIVE = Category(
    uuid=UUID("9eb0db06-a437-4301-8a4c-7a0c753dfba4"),
    label="//regulation/negative",
)
Category.REGULATION_POSITIVE = Category(
    uuid=UUID("0de37d73-6dd4-49c9-9e41-b8fc213fea8f"),
    label="//regulation/positive",
)
Category.REGULATION_UNKNOWN = Category(
    uuid=UUID("a87f0118-57ff-41dc-90c5-30fdf94e7acd"),
    label="//regulation/unknown",
)
Category.REGULATOR = Category(
    uuid=UUID("324391a8-76c0-4d21-9050-430358583c2e"),
    label="regulator",
)
Category.RIBOSOME = Category(
    uuid=UUID("c248bea8-1d37-4921-ab0f-23457646294f"),
    label="//ribosome",
)
Category.RIBOSOME_EUKARYOTE = Category(
    uuid=UUID("8654eb8e-54b8-4eb5-aeba-a896d6485e3c"),
    label="//ribosome/eukaryote",
)
Category.RIBOSOME_EUKARYOTE_YEAST = Category(
    uuid=UUID("ff73d9e5-963c-4988-8a55-e6f2e2f7cf2b"),
    label="//ribosome/eukaryote/yeast",
)
Category.RIBOSOME_PROKARYOTE = Category(
    uuid=UUID("7a2105f1-2956-4405-bfcb-bf1bd6ab4ca4"),
    label="//ribosome/prokaryote",
)
Category.RIBOSOME_PROKARYOTE_BCEPACIA = Category(
    uuid=UUID("e6d6751d-eb92-4d1a-a931-404df05955f3"),
    label="//ribosome/prokaryote/bcepacia",
)
Category.RIBOSOME_PROKARYOTE_BSUBTILIS = Category(
    uuid=UUID("2c2bca0d-162e-4424-8ef7-35a49b16ac58"),
    label="//ribosome/prokaryote/bsubtilis",
)
Category.RIBOSOME_PROKARYOTE_CUSTOM = Category(
    uuid=UUID("afd62f2f-b9a0-4c7a-9043-7c65a4b032e3"),
    label="//ribosome/prokaryote/custom",
)
Category.RIBOSOME_PROKARYOTE_ECOLI = Category(
    uuid=UUID("24f30567-68aa-407a-a197-286f16f57fb1"),
    label="//ribosome/prokaryote/ecoli",
)
Category.RIBOSOME_PROKARYOTE_PANANATIS = Category(
    uuid=UUID("3bb3664a-11ea-45ea-abda-836a34281dfa"),
    label="//ribosome/prokaryote/pananatis",
)
Category.RIBOSOME_PROKARYOTE_PPUTIDA = Category(
    uuid=UUID("560cef8e-396c-4f7d-bb3b-5adc85d57f3e"),
    label="//ribosome/prokaryote/pputida",
)
Category.RIBOSOME_PROKARYOTE_SALMONELLA = Category(
    uuid=UUID("8cf0504c-1cea-4f77-b7a8-125065d723d3"),
    label="//ribosome/prokaryote/salmonella",
)
Category.RIBOSOME_PROKARYOTE_SESPANAENSIS = Category(
    uuid=UUID("3320df88-aeb1-4948-9571-2abc336e08bc"),
    label="//ribosome/prokaryote/sespanaensis",
)
Category.RNA = Category(
    uuid=UUID("a36b7509-ecb1-4157-b540-82acc1517884"),
    label="//rna",
)
Category.RNA_APTAMER = Category(
    uuid=UUID("6ede57b6-230b-4149-80c6-c412d004e2e4"),
    label="//rna/aptamer",
)
Category.RNA_APTAZYME = Category(
    uuid=UUID("2a8c99bd-f6f0-4968-b9aa-87d0e39c0529"),
    label="//rna/aptazyme",
)
Category.RNAP = Category(
    uuid=UUID("ed031f93-523c-4d78-b413-4516d6ded237"),
    label="//rnap",
)
Category.RNAP_BACTERIOPHAGE_SP6 = Category(
    uuid=UUID("9a1829fa-8960-4208-98f5-bc6fff17bb0e"),
    label="//rnap/bacteriophage/sp6",
)
Category.RNAP_BACTERIOPHAGE_T3 = Category(
    uuid=UUID("1e4d13b0-8350-47b3-8d06-3da3a1b7e69e"),
    label="//rnap/bacteriophage/t3",
)
Category.RNAP_BACTERIOPHAGE_T7 = Category(
    uuid=UUID("ad740bdf-561a-41c0-800a-ee8d3f80b1c0"),
    label="//rnap/bacteriophage/t7",
)
Category.RNAP_EUKARYOTE = Category(
    uuid=UUID("03c4fc77-639a-4c85-bff6-e3d0eacbb415"),
    label="//rnap/eukaryote",
)
Category.RNAP_EUKARYOTE_PICHIA = Category(
    uuid=UUID("2bfd326c-87bc-4c6f-af4a-77e7674576bf"),
    label="//rnap/eukaryote/pichia",
)
Category.RNAP_EUKARYOTE_YEAST = Category(
    uuid=UUID("9c063237-bae2-401c-8aaa-e9820cca7b56"),
    label="//rnap/eukaryote/yeast",
)
Category.RNAP_MISCELLANEOUS = Category(
    uuid=UUID("c81d9bc1-ee1b-4af8-a39f-9cb1cc912415"),
    label="//rnap/miscellaneous",
)
Category.RNAP_PROKARYOTE = Category(
    uuid=UUID("9f2856a5-ec5e-498e-bd68-4524db3faddf"),
    label="//rnap/prokaryote",
)
Category.RNAP_PROKARYOTE_AFERROOXIDANS = Category(
    uuid=UUID("4162b2c8-99a2-4069-b8f4-34af99914f19"),
    label="//rnap/prokaryote/aferrooxidans",
)
Category.RNAP_PROKARYOTE_ECOLI = Category(
    uuid=UUID("9c63e0dc-052c-4ade-970d-f075aaf3956a"),
    label="//rnap/prokaryote/ecoli",
)
Category.RNAP_PROKARYOTE_ECOLI_SIGMA24 = Category(
    uuid=UUID("621a38c0-2016-4265-af4f-fd3a951686cd"),
    label="//rnap/prokaryote/ecoli/sigma24",
)
Category.RNAP_PROKARYOTE_ECOLI_SIGMA25 = Category(
    uuid=UUID("505638ab-dc51-441d-8107-5c81880abe96"),
    label="//rnap/prokaryote/ecoli/sigma25",
)
Category.RNAP_PROKARYOTE_ECOLI_SIGMA32 = Category(
    uuid=UUID("97c54bc3-c58a-46f0-acaf-23e28f3fb874"),
    label="//rnap/prokaryote/ecoli/sigma32",
)
Category.RNAP_PROKARYOTE_ECOLI_SIGMA54 = Category(
    uuid=UUID("75e61371-a9a9-4482-8dda-8ea0470a2c45"),
    label="//rnap/prokaryote/ecoli/sigma54",
)
Category.RNAP_PROKARYOTE_ECOLI_SIGMA70 = Category(
    uuid=UUID("f4a08539-a3d8-4f90-9ca7-25ecf57a1e2f"),
    label="//rnap/prokaryote/ecoli/sigma70",
)
Category.RNAP_PROKARYOTE_ECOLI_SIGMAS = Category(
    uuid=UUID("b44dbb4e-37ac-40be-9cf2-52349dd67787"),
    label="//rnap/prokaryote/ecoli/sigmas",
)
Category.RNAP_PROKARYOTE_PMIRABILIS = Category(
    uuid=UUID("26dde76f-c282-41c4-91c4-a5d2d1f085d6"),
    label="//rnap/prokaryote/pmirabilis",
)
Category.RNAP_PROKARYOTE_PPUTIDA = Category(
    uuid=UUID("319cb74b-76ab-4d5e-bad3-846bbdacd71e"),
    label="//rnap/prokaryote/pputida",
)
Category.RNAP_PROKARYOTE_REUPHORA = Category(
    uuid=UUID("f4bd4599-b0eb-4b27-86c9-2bc5f042052e"),
    label="//rnap/prokaryote/reuphora",
)
Category.RNAP_PROKARYOTE_SALMONELLA = Category(
    uuid=UUID("540cd845-cd1d-4b42-bf16-0d467013bd29"),
    label="//rnap/prokaryote/salmonella",
)
Category.RNAP_PROKARYOTE_SUBTILIS_SIGMAA = Category(
    uuid=UUID("df33683e-e154-4fdb-973f-6e91a586ac83"),
    label="//rnap/prokaryote/subtilis/sigmaa",
)
Category.RNAP_PROKARYOTE_SUBTILIS_SIGMAB = Category(
    uuid=UUID("c5f8d730-78a2-4d85-bfd5-6ae3472fa0a5"),
    label="//rnap/prokaryote/subtilis/sigmab",
)
Category.RNAP_PROKARYOTE_SYNECHOCYSTIS = Category(
    uuid=UUID("7541d37d-d635-467d-b60f-18fef4cb43cb"),
    label="//rnap/prokaryote/synechocystis",
)
Category.RNAP_PROKARYOTE_VHARVEYI_SIGMA54 = Category(
    uuid=UUID("8ee203c9-62b1-424c-88a6-a0209df486d2"),
    label="//rnap/prokaryote/vharveyi/sigma54",
)
Category.RNA_RIBOSWITCH = Category(
    uuid=UUID("a1ddf64f-c71b-4c44-bd9c-a8aeb2faa571"),
    label="//rna/riboswitch",
)
Category.RNA_RIBOZYME = Category(
    uuid=UUID("331f7456-bb5d-412a-ad30-b57467108359"),
    label="//rna/ribozyme",
)
Category.T3 = Category(
    uuid=UUID("e62206a5-c020-43eb-841e-bcfe1eefaade"),
    label="//t3",
)
Category.T3_T2 = Category(
    uuid=UUID("9a125372-b918-455b-b54b-7a2836557540"),
    label="//t3/t2",
)
Category.T3_T4 = Category(
    uuid=UUID("b2ad60ec-b26d-4785-bb45-af2dfa426b57"),
    label="//t3/t4",
)
Category.TERMINATOR = Category(
    uuid=UUID("cbed5b9e-a463-4a9d-8da5-1f20afa37477"),
    label="//terminator",
)
Category.TERMINATOR_DOUBLE = Category(
    uuid=UUID("6c13ed1a-6baa-4622-98fa-df46bd97b1b8"),
    label="//terminator/double",
)
Category.TERMINATOR_SINGLE = Category(
    uuid=UUID("d291cffb-eb9f-406a-b8af-faff1ca025fc"),
    label="//terminator/single",
)
Category.TRANSCRIPTIONAL = Category(
    uuid=UUID("099664e0-f93a-4f6c-897c-8675078a64f4"),
    label="transcriptional",
)
Category.VIRAL_VECTORS = Category(
    uuid=UUID("35beebc7-14fe-4073-a874-099863897d0a"),
    label="//viral_vectors",
)
Category.VIRAL_VECTORS_AAV = Category(
    uuid=UUID("a9ab2ceb-99ca-4c6b-964a-1707a50b1a2f"),
    label="//viral_vectors/aav",
)
Category.VIRAL_VECTORS_AAV_CAPSID_CODING = Category(
    uuid=UUID("0a396a52-d7bb-4597-8464-c7f756e51243"),
    label="//viral_vectors/aav/capsid_coding",
)
Category.VIRAL_VECTORS_AAV_MISCELLANEOUS = Category(
    uuid=UUID("41e6b868-877a-4ccb-8b7e-90330e0fae5b"),
    label="//viral_vectors/aav/miscellaneous",
)
Category.VIRAL_VECTORS_AAV_VECTOR_PLASMID = Category(
    uuid=UUID("49c3eab1-4649-4527-8145-d62599e23edc"),
    label="//viral_vectors/aav/vector_plasmid",
)

Category.CATALOG = {
    str(key): value
    for value in [
        Category.BINDING_CELLULOSE,
        Category.BINDING_METAL,
        Category.BIOSAFETY,
        Category.BIOSAFETY_KILL_SWITCH,
        Category.BIOSAFETY_SEMANTIC_CONTAINMENT,
        Category.BIOSAFETY_XNASE,
        Category.CDS,
        Category.CDS_BIOSYNTHESIS,
        Category.CDS_BIOSYNTHESIS_ANTHOCYANINS,
        Category.CDS_CHROMATINREMODELING,
        Category.CDS_ENZYME,
        Category.CDS_ENZYME_CHROMATINREMODELING,
        Category.CDS_ENZYME_DNAPOLYMERASE,
        Category.CDS_ENZYME_DNASE,
        Category.CDS_ENZYME_ENDONUCLEASE,
        Category.CDS_ENZYME_ENDONUCLEASE_RESTRICTION,
        Category.CDS_ENZYME_EXONUCLEASE,
        Category.CDS_ENZYME_LIGASE,
        Category.CDS_ENZYME_LYSIS,
        Category.CDS_ENZYME_METHYLATION,
        Category.CDS_ENZYME_PHOSPHORYLATION,
        Category.CDS_ENZYME_PROTEASE,
        Category.CDS_ENZYME_RNAP,
        Category.CDS_ENZYME_RNAPOLYMERASE,
        Category.CDS_LIGAND,
        Category.CDS_LYSIS,
        Category.CDS_MEMBRANE,
        Category.CDS_MEMBRANE_CHANNEL,
        Category.CDS_MEMBRANE_EXTRACELLULAR,
        Category.CDS_MEMBRANE_LYSIS,
        Category.CDS_MEMBRANE_PUMP,
        Category.CDS_MEMBRANE_RECEPTOR,
        Category.CDS_MEMBRANE_TRANSPORTER,
        Category.CDS_RECEPTOR,
        Category.CDS_RECEPTOR_ANTIBODY,
        Category.CDS_REPORTER,
        Category.CDS_REPORTER_CFP,
        Category.CDS_REPORTER_CHROMOPROTEIN,
        Category.CDS_REPORTER_GFP,
        Category.CDS_REPORTER_RFP,
        Category.CDS_REPORTER_YFP,
        Category.CDS_SELECTIONMARKER,
        Category.CDS_SELECTIONMARKER_ANTIBIOTICRESISTANCE,
        Category.CDS_TRANSCRIPTIONALREGULATOR,
        Category.CDS_TRANSCRIPTIONALREGULATOR_ACTIVATOR,
        Category.CDS_TRANSCRIPTIONALREGULATOR_REPRESSOR,
        Category.CHASSIS,
        Category.CHASSIS_AFERROOXIDANS,
        Category.CHASSIS_BACTERIOPHAGE,
        Category.CHASSIS_BACTERIOPHAGE_T3,
        Category.CHASSIS_BACTERIOPHAGE_T4,
        Category.CHASSIS_BACTERIOPHAGE_T7,
        Category.CHASSIS_EUKARYOTE,
        Category.CHASSIS_EUKARYOTE_ATHALIANA,
        Category.CHASSIS_EUKARYOTE_HUMAN,
        Category.CHASSIS_EUKARYOTE_MPOLYMORPHA,
        Category.CHASSIS_EUKARYOTE_NBENTHAMIANA,
        Category.CHASSIS_EUKARYOTE_NTABACUM,
        Category.CHASSIS_EUKARYOTE_PICHIA,
        Category.CHASSIS_EUKARYOTE_PLANTS_OTHER,
        Category.CHASSIS_EUKARYOTE_PPATENS,
        Category.CHASSIS_EUKARYOTE_YEAST,
        Category.CHASSIS_MISCELLANEOUS,
        Category.CHASSIS_MULTIHOST,
        Category.CHASSIS_ORGANELLE,
        Category.CHASSIS_ORGANELLE_CHLOROPLAST,
        Category.CHASSIS_ORGANELLE_MITOCHONDRION,
        Category.CHASSIS_PROKARYOTE,
        Category.CHASSIS_PROKARYOTE_BCEPACIA,
        Category.CHASSIS_PROKARYOTE_BSUBTILIS,
        Category.CHASSIS_PROKARYOTE_CYANOBACTERIUM,
        Category.CHASSIS_PROKARYOTE_ECOLI,
        Category.CHASSIS_PROKARYOTE_ECOLI_NISSLE,
        Category.CHASSIS_PROKARYOTE_GXYLINUS,
        Category.CHASSIS_PROKARYOTE_LACTOBACILLUS,
        Category.CHASSIS_PROKARYOTE_LACTOCOCCUS,
        Category.CHASSIS_PROKARYOTE_MFLORUM,
        Category.CHASSIS_PROKARYOTE_PANANATIS,
        Category.CHASSIS_PROKARYOTE_PMIRABILIS,
        Category.CHASSIS_PROKARYOTE_PPUTIDA,
        Category.CHASSIS_PROKARYOTE_REUPHORA,
        Category.CHASSIS_PROKARYOTE_RRADIOBACTER,
        Category.CHASSIS_PROKARYOTE_SALMONELLA,
        Category.CHASSIS_PROKARYOTE_SESPANAENSIS,
        Category.CHASSIS_PROKARYOTE_SUBTILIS,
        Category.CHASSIS_PROKARYOTE_SYNECHOCYSTIS,
        Category.CHASSIS_PROKARYOTE_VHARVEYI,
        Category.CLASSIC_COMPOSITE_UNCATEGORIZED,
        Category.CLASSIC_DEVICE_UNCATEGORIZED,
        Category.CLASSIC_GENERATOR_PLASMIDS,
        Category.CLASSIC_GENERATOR_PRC,
        Category.CLASSIC_GENERATOR_PRCT,
        Category.CLASSIC_GENERATOR_RC,
        Category.CLASSIC_GENERATOR_RCT,
        Category.CLASSIC_GENERATOR_UNCATEGORIZED,
        Category.CLASSIC_INTERMEDIATE_UNCATEGORIZED,
        Category.CLASSIC_INVERTER_UNCATEGORIZED,
        Category.CLASSIC_MEASUREMENT_O_H,
        Category.CLASSIC_MEASUREMENT_UNCATEGORIZED,
        Category.CLASSIC_OTHER_UNCATEGORIZED,
        Category.CLASSIC_PLASMID_MEASUREMENT,
        Category.CLASSIC_PLASMID_UNCATEGORIZED,
        Category.CLASSIC_PROJECT_UNCATEGORIZED,
        Category.CLASSIC_RBS_UNCATEGORIZED,
        Category.CLASSIC_REGULATORY_OTHER,
        Category.CLASSIC_REGULATORY_UNCATEGORIZED,
        Category.CLASSIC_REPORTER,
        Category.CLASSIC_REPORTER_CONSTITUTIVE,
        Category.CLASSIC_REPORTER_MULTIPLE,
        Category.CLASSIC_REPORTER_PRET,
        Category.CLASSIC_REPORTER_RET,
        Category.CLASSIC_RNA_UNCATEGORIZED,
        Category.CLASSIC_SIGNALLING_RECEIVER,
        Category.CLASSIC_SIGNALLING_SENDER,
        Category.CLASSIC_TEMPORARY_UNCATEGORIZED,
        Category.DIRECTION,
        Category.DIRECTION_BIDIRECTIONAL,
        Category.DIRECTION_FORWARD,
        Category.DIRECTION_REVERSE,
        Category.DNA,
        Category.DNA_APTAMER,
        Category.DNA_BIOSCAFFOLD,
        Category.DNA_CHROMOSOMALINTEGRATION,
        Category.DNA_CLONINGSITE,
        Category.DNA_CONJUGATION,
        Category.DNA_DNAZYME,
        Category.DNA_NUCLEOTIDE,
        Category.DNA_ORIGAMI,
        Category.DNA_ORIGIN_OF_REPLICATION,
        Category.DNA_PRIMERBINDINGSITE,
        Category.DNA_RESTRICTIONSITE,
        Category.DNA_SCAR,
        Category.DNA_SPACER,
        Category.DNA_TRANSPOSOME_TN5,
        Category.DNA_TRANSPOSON,
        Category.EXTREMOPHILES,
        Category.FUNCTION_BIOFUELS,
        Category.FUNCTION_BIOSYNTHESIS,
        Category.FUNCTION_BIOSYNTHESIS_AHL,
        Category.FUNCTION_BIOSYNTHESIS_BUTANOL,
        Category.FUNCTION_BIOSYNTHESIS_CELLULOSE,
        Category.FUNCTION_BIOSYNTHESIS_HEME,
        Category.FUNCTION_BIOSYNTHESIS_ISOPRENOID,
        Category.FUNCTION_BIOSYNTHESIS_ODORANT,
        Category.FUNCTION_BIOSYNTHESIS_PHYCOCYANOBILIN,
        Category.FUNCTION_BIOSYNTHESIS_PLASTIC,
        Category.FUNCTION_BIOSYNTHESIS_PYOCYANIN,
        Category.FUNCTION_CELLDEATH,
        Category.FUNCTION_CELLSIGNALLING,
        Category.FUNCTION_COLIROID,
        Category.FUNCTION_CONJUGATION,
        Category.FUNCTION_CRISPR,
        Category.FUNCTION_CRISPR_CAS,
        Category.FUNCTION_CRISPR_CAS9,
        Category.FUNCTION_CRISPR_GRNA,
        Category.FUNCTION_CRISPR_GRNA_CONSTRUCT,
        Category.FUNCTION_CRISPR_GRNA_EFFICIENT,
        Category.FUNCTION_CRISPR_GRNA_REPEAT,
        Category.FUNCTION_CRISPR_GRNA_SPACER,
        Category.FUNCTION_DEGRADATION,
        Category.FUNCTION_DEGRADATION_AHL,
        Category.FUNCTION_DEGRADATION_BISPHENOL,
        Category.FUNCTION_DEGRADATION_CELLULOSE,
        Category.FUNCTION_DNA,
        Category.FUNCTION_FRET,
        Category.FUNCTION_IMMUNOLOGY,
        Category.FUNCTION_MISMATCHREPAIR,
        Category.FUNCTION_MOTILITY,
        Category.FUNCTION_ODOR,
        Category.FUNCTION_RECOMBINATION,
        Category.FUNCTION_RECOMBINATION_CRE,
        Category.FUNCTION_RECOMBINATION_FIM,
        Category.FUNCTION_RECOMBINATION_FLP,
        Category.FUNCTION_RECOMBINATION_HIN,
        Category.FUNCTION_RECOMBINATION_LAMBDA,
        Category.FUNCTION_RECOMBINATION_P22,
        Category.FUNCTION_RECOMBINATION_XER,
        Category.FUNCTION_REGULATION_TRANSCRIPTIONAL,
        Category.FUNCTION_REPORTER,
        Category.FUNCTION_REPORTER_COLOR,
        Category.FUNCTION_REPORTER_FLUORESCENCE,
        Category.FUNCTION_REPORTER_LIGHT,
        Category.FUNCTION_REPORTER_PIGMENT,
        Category.FUNCTION_SENSOR,
        Category.FUNCTION_SENSOR_LEAD,
        Category.FUNCTION_SENSOR_LIGHT,
        Category.FUNCTION_SENSOR_METAL,
        Category.FUNCTION_STRUCTURES,
        Category.FUNCTION_TUMORKILLINGBACTERIA,
        Category.PLASMID,
        Category.PLASMIDBACKBONE,
        Category.PLASMIDBACKBONE_ARCHIVE,
        Category.PLASMIDBACKBONE_ASSEMBLY,
        Category.PLASMIDBACKBONE_ASSEMBLY_TYPEIIS,
        Category.PLASMIDBACKBONE_COMPONENT_DEFAULTINSERT,
        Category.PLASMIDBACKBONE_COMPONENT_SELECTIONMARKER_ANTIBIOTICRESISTANCE,
        Category.PLASMIDBACKBONE_COPYNUMBER,
        Category.PLASMIDBACKBONE_COPYNUMBER_HIGH,
        Category.PLASMIDBACKBONE_COPYNUMBER_INDUCIBLE,
        Category.PLASMIDBACKBONE_COPYNUMBER_LOW,
        Category.PLASMIDBACKBONE_COPYNUMBER_MEDIUM,
        Category.PLASMIDBACKBONE_EXPRESSION,
        Category.PLASMIDBACKBONE_EXPRESSION_CONSTITUTIVE,
        Category.PLASMIDBACKBONE_EXPRESSION_INDUCIBLE,
        Category.PLASMIDBACKBONE_LIBRARYSCREENING,
        Category.PLASMIDBACKBONE_LIBRARYSCREENING_CODINGSEQUENCE,
        Category.PLASMIDBACKBONE_LIBRARYSCREENING_PROMOTER,
        Category.PLASMIDBACKBONE_LIBRARYSCREENING_RBSCODINGSEQUENCE,
        Category.PLASMIDBACKBONE_OPERATION,
        Category.PLASMIDBACKBONE_PROTEINFUSION,
        Category.PLASMIDBACKBONE_SYNTHESIS,
        Category.PLASMIDBACKBONE_VERSION_10,
        Category.PLASMIDBACKBONE_VERSION_3,
        Category.PLASMIDBACKBONE_VERSION_4,
        Category.PLASMIDBACKBONE_VERSION_5,
        Category.PLASMID_CHROMOSOMALINTEGRATION,
        Category.PLASMID_COMPONENT_CLONINGSITE,
        Category.PLASMID_COMPONENT_INSULATION,
        Category.PLASMID_COMPONENT_ORIGIN,
        Category.PLASMID_COMPONENT_OTHER,
        Category.PLASMID_COMPONENT_PRIMERBINDINGSITE,
        Category.PLASMID_CONSTRUCTION,
        Category.PLASMID_EXPRESSION,
        Category.PLASMID_EXPRESSION_T7,
        Category.PLASMID_MEASUREMENT,
        Category.PLASMID_SP6,
        Category.PRIMER_M13,
        Category.PRIMER_PART,
        Category.PRIMER_PART_AMPLIFICATION,
        Category.PRIMER_PART_SEQUENCING,
        Category.PRIMER_PLASMID_AMPLIFICATION,
        Category.PRIMER_REPORTER_CFP,
        Category.PRIMER_REPORTER_GFP,
        Category.PRIMER_REPORTER_YFP,
        Category.PRIMER_SP6,
        Category.PRIMER_T3,
        Category.PRIMER_T7,
        Category.PROMOTER,
        Category.PROMOTER_ANDERSON,
        Category.PROMOTER_IRON,
        Category.PROMOTER_LOGIC_USTC,
        Category.PROMOTER_STRESSKIT,
        Category.PROTEINDOMAIN,
        Category.PROTEINDOMAIN_ACTIVATION,
        Category.PROTEINDOMAIN_AFFINITY,
        Category.PROTEINDOMAIN_BINDING,
        Category.PROTEINDOMAIN_BINDING_CELLULOSE,
        Category.PROTEINDOMAIN_CLEAVAGE,
        Category.PROTEINDOMAIN_DEGRADATION,
        Category.PROTEINDOMAIN_DNABINDING,
        Category.PROTEINDOMAIN_HEAD,
        Category.PROTEINDOMAIN_INTERNAL,
        Category.PROTEINDOMAIN_INTERNAL_SPECIAL,
        Category.PROTEINDOMAIN_LINKER,
        Category.PROTEINDOMAIN_LOCALIZATION,
        Category.PROTEINDOMAIN_REPRESSION,
        Category.PROTEINDOMAIN_TAIL,
        Category.PROTEINDOMAIN_TRANSMEMBRANE,
        Category.RBS_PROKARYOTE,
        Category.RBS_PROKARYOTE_CONSTITUTIVE,
        Category.RBS_PROKARYOTE_CONSTITUTIVE_ANDERSON,
        Category.RBS_PROKARYOTE_CONSTITUTIVE_COMMUNITY,
        Category.RBS_PROKARYOTE_CONSTITUTIVE_CONSTITUTIVE,
        Category.RBS_PROKARYOTE_CONSTITUTIVE_MISCELLANEOUS,
        Category.RBS_PROKARYOTE_CONSTITUTIVE_RACKHAM,
        Category.RBS_PROKARYOTE_REGULATED_ISSACS,
        Category.RBS_PROKARYOTIC_CONSTITUTIVE_MISCELLANEOUS,
        Category.RECEIVER,
        Category.REGULATION,
        Category.REGULATION_CONSTITUTIVE,
        Category.REGULATION_MULTIPLE,
        Category.REGULATION_NEGATIVE,
        Category.REGULATION_POSITIVE,
        Category.REGULATION_UNKNOWN,
        Category.REGULATOR,
        Category.RIBOSOME,
        Category.RIBOSOME_EUKARYOTE,
        Category.RIBOSOME_EUKARYOTE_YEAST,
        Category.RIBOSOME_PROKARYOTE,
        Category.RIBOSOME_PROKARYOTE_BCEPACIA,
        Category.RIBOSOME_PROKARYOTE_BSUBTILIS,
        Category.RIBOSOME_PROKARYOTE_CUSTOM,
        Category.RIBOSOME_PROKARYOTE_ECOLI,
        Category.RIBOSOME_PROKARYOTE_PANANATIS,
        Category.RIBOSOME_PROKARYOTE_PPUTIDA,
        Category.RIBOSOME_PROKARYOTE_SALMONELLA,
        Category.RIBOSOME_PROKARYOTE_SESPANAENSIS,
        Category.RNA,
        Category.RNA_APTAMER,
        Category.RNA_APTAZYME,
        Category.RNAP,
        Category.RNAP_BACTERIOPHAGE_SP6,
        Category.RNAP_BACTERIOPHAGE_T3,
        Category.RNAP_BACTERIOPHAGE_T7,
        Category.RNAP_EUKARYOTE,
        Category.RNAP_EUKARYOTE_PICHIA,
        Category.RNAP_EUKARYOTE_YEAST,
        Category.RNAP_MISCELLANEOUS,
        Category.RNAP_PROKARYOTE,
        Category.RNAP_PROKARYOTE_AFERROOXIDANS,
        Category.RNAP_PROKARYOTE_ECOLI,
        Category.RNAP_PROKARYOTE_ECOLI_SIGMA24,
        Category.RNAP_PROKARYOTE_ECOLI_SIGMA25,
        Category.RNAP_PROKARYOTE_ECOLI_SIGMA32,
        Category.RNAP_PROKARYOTE_ECOLI_SIGMA54,
        Category.RNAP_PROKARYOTE_ECOLI_SIGMA70,
        Category.RNAP_PROKARYOTE_ECOLI_SIGMAS,
        Category.RNAP_PROKARYOTE_PMIRABILIS,
        Category.RNAP_PROKARYOTE_PPUTIDA,
        Category.RNAP_PROKARYOTE_REUPHORA,
        Category.RNAP_PROKARYOTE_SALMONELLA,
        Category.RNAP_PROKARYOTE_SUBTILIS_SIGMAA,
        Category.RNAP_PROKARYOTE_SUBTILIS_SIGMAB,
        Category.RNAP_PROKARYOTE_SYNECHOCYSTIS,
        Category.RNAP_PROKARYOTE_VHARVEYI_SIGMA54,
        Category.RNA_RIBOSWITCH,
        Category.RNA_RIBOZYME,
        Category.T3,
        Category.T3_T2,
        Category.T3_T4,
        Category.TERMINATOR,
        Category.TERMINATOR_DOUBLE,
        Category.TERMINATOR_SINGLE,
        Category.TRANSCRIPTIONAL,
        Category.VIRAL_VECTORS,
        Category.VIRAL_VECTORS_AAV,
        Category.VIRAL_VECTORS_AAV_CAPSID_CODING,
        Category.VIRAL_VECTORS_AAV_MISCELLANEOUS,
        Category.VIRAL_VECTORS_AAV_VECTOR_PLASMID,
    ]
    for key in (value.uuid, value.label)
}
