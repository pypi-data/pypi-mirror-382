"""Common schema primitives.

This submodule defines common Pydantic models, enums, and protocols used
throughout the package.

Exports:
    LockedModel: Model with immutable fields.
    DynamicModel: Model with mutable fields.
    AuditLog: Audit log entry model.
    CleanEnum: Enum with clean representation.
    Progress: Protocol for reporting fetch progress.
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from enum import Enum
from typing import Protocol

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

__all__: list[str] = [
    "AuditLog",
    "CleanEnum",
    "DynamicModel",
    "LockedModel",
    "Progress",
]


class LockedModel(BaseModel):
    """Model with immutable fields.

    Represents a resource where attributes remain frozen (read-only) after
    initialization.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        validate_by_name=True,
        validate_by_alias=True,
        use_enum_values=False,
        arbitrary_types_allowed=True,
    )


class DynamicModel(BaseModel):
    """Model with mutable fields.

    Represents a resource where attributes can be modified after
    initialization.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        validate_assignment=True,
        validate_by_name=True,
        validate_by_alias=True,
        use_enum_values=False,
        arbitrary_types_allowed=True,
    )


class AuditLog(LockedModel):
    """Audit log entry.

    Represents a record of changes made to a resource.

    Attributes:
        created (datetime): Timestamp when the entry was created.
        updated (datetime): Timestamp when the entry was last updated.

    """

    created: datetime = Field(
        title="Created",
        description="ISO 8601 timestamp when the entity was created.",
    )
    updated: datetime = Field(
        title="Updated",
        description="ISO 8601 timestamp when the entity was last updated.",
    )


class CleanEnum(Enum):
    """Enum with clean representation.

    Provides a more readable string representation for enum members.
    """

    def __repr__(self) -> str:
        """Return member representation in `Class.Member` format."""
        return f"{self.__class__.__name__}.{self.name}"

    def __str__(self) -> str:
        """Return member representation in `Class.Member` format."""
        return f"{self.__class__.__name__}.{self.name}"


class Progress(Protocol):
    """Progress reporter for paginated fetches.

    Args:
        current (int): Number of items fetched (monotonic non-decreasing).
        total (int | None): Total item count if available, otherwise None. When
           a `limit` is provided by the caller, `total` equals that limit.

    """

    def __call__(self, current: int, total: int | None) -> None:
        """Report progress of a paginated fetch."""
        ...
