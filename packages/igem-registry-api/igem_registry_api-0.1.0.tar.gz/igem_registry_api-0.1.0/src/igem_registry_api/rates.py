"""API rate limit utilities.

This submodule provides helpers to read per-window rate-limits from HTTP
response headers and to compute a suitable cooldown period when limits have
been reached.

Exports:
    RateLimit: Model representing rate-limit information.
    ratelimit: Parses rate-limit information from response headers.
    cooldown: Computes a wait (seconds) based on current limits.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, cast

from pydantic import Field, NonNegativeInt

from .schemas import LockedModel

if TYPE_CHECKING:
    from requests.structures import CaseInsensitiveDict


WINDOWS: tuple[str, str, str] = ("short", "medium", "large")
METRICS: tuple[str, str, str] = ("remaining", "reset", "limit")

RATE_LIMIT_HEADERS: tuple[tuple[str, ...], ...] = tuple(
    tuple(f"x-ratelimit-{metric}-{window}" for window in WINDOWS)
    for metric in METRICS
)
RETRY_AFTER_HEADERS: tuple[str, ...] = tuple(
    f"retry-after-{window}" for window in WINDOWS
)


__all__: list[str] = [
    "RateLimit",
    "cooldown",
    "ratelimit",
]


WindowTriple = tuple[NonNegativeInt, NonNegativeInt, NonNegativeInt]


class RateLimit(LockedModel):
    """Rate limit information.

    Represents the rate limits imposed by the API for different call windows.

    Attributes:
        balance (WindowTriple): Remaining requests for short, medium, and large
            call windows.
        reset (WindowTriple): Reset times (in seconds) for short, medium, and
            large call windows.
        quota (WindowTriple): Request limits for short, medium, and large call
            windows.

    """

    balance: Annotated[
        WindowTriple,
        Field(
            title="Balance",
            description=(
                "Remaining requests for short, medium, and large call windows."
            ),
            alias="remaining",
        ),
    ] = (0, 0, 0)
    reset: Annotated[
        WindowTriple,
        Field(
            title="Reset",
            description=(
                "Reset times for short, medium, and large call windows."
            ),
            alias="reset",
        ),
    ] = (5, 60, 600)
    quota: Annotated[
        WindowTriple,
        Field(
            title="Quota",
            description=(
                "Request limits for short, medium, and large call windows."
            ),
            alias="limit",
        ),
    ] = (5, 60, 200)


def ratelimit(
    headers: CaseInsensitiveDict,
) -> RateLimit:
    """Extract rate limit information from response headers.

    Args:
        headers (CaseInsensitiveDict): The response headers from which to
            extract rate limit information.

    Returns:
        out (RateLimit): Extracted rate limit information.

    """
    data = {}

    if all(header in headers for lot in RATE_LIMIT_HEADERS for header in lot):
        for metric, lot in zip(METRICS, RATE_LIMIT_HEADERS, strict=True):
            data[metric] = tuple(int(headers.get(header, 1)) for header in lot)
    elif any(header in headers for header in RETRY_AFTER_HEADERS):
        data["reset"] = tuple(
            int(headers.get(header, 1)) for header in RETRY_AFTER_HEADERS
        )
    else:
        data["reset"] = (1, 1, 1)

    data = cast("dict[str, WindowTriple]", data)

    return RateLimit(**data)


def cooldown(ratelimit: RateLimit) -> NonNegativeInt:
    """Calculate the cooldown duration based on the rate limit information.

    Args:
        ratelimit (RateLimit): The rate limit information to use for
            calculating the cooldown.

    Returns:
        out (NonNegativeInt): The calculated cooldown duration (seconds).

    """
    waits = [
        time
        for calls, time in zip(
            ratelimit.balance,
            ratelimit.reset,
            strict=False,
        )
        if calls == 0
    ]
    return max(waits, default=0)
