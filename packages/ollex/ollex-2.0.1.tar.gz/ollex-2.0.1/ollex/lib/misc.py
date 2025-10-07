"""Miscellaneous utility functions."""

from __future__ import annotations

from collections.abc import Iterator


# ------------------------------------------------------------------------------
def chunk_list(ll: list, max_len: int) -> Iterator[list]:
    """Split a list into chunks with a maximum specified length."""

    for i in range(0, len(ll), max_len):
        yield ll[i : i + max_len]


# ------------------------------------------------------------------------------
def plural(s: str, n: int) -> str:
    """Pluralise a string."""

    return s if n == 1 else f'{s}s'
