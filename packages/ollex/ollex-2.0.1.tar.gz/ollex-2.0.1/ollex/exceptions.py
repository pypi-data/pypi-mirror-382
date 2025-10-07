"""Ollex exceptions."""

from __future__ import annotations


class OllexError(Exception):
    """Base class for ollex errors."""

    pass


class OllexInternalError(OllexError):
    """Internal error."""

    def __str__(self):
        """Get string representation."""

        return f'Internal error: {", ".join(str(s) for s in self.args)}'
