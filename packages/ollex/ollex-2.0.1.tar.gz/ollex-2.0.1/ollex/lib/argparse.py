"""Argument parsing."""

from __future__ import annotations

from argparse import Action, ArgumentError, ArgumentParser
from typing import Any


# ------------------------------------------------------------------------------
class StoreNameValuePair(Action):
    """
    Used with argparse to store values from options of the form ``--option name=value``.

    The destination (self.dest) will be created as a dict {name: value}. This
    allows multiple name-value pairs to be set for the same option.

    Usage is:

    ::

        argparser.add_argument('-x', metavar='key=value', action=StoreNameValuePair)

    or

    ::

        argparser.add_argument('-x', metavar='key=value ...', action=StoreNameValuePair, nargs='+')

    """

    # --------------------------------------------------------------------------
    # noinspection PyUnresolvedReferences
    def __call__(self, parser, namespace, values, option_string=None):
        """Handle name=value option."""

        if not hasattr(namespace, self.dest) or not getattr(namespace, self.dest):
            setattr(namespace, self.dest, {})
        argdict = getattr(namespace, self.dest)

        if not isinstance(values, list):
            values = [values]
        for val in values:
            try:
                n, v = val.split('=', 1)
            except ValueError:
                raise ArgumentError(self, f'Expected "key=value", got "{val}"')
            argdict[n] = v


# ------------------------------------------------------------------------------
class ReplArgparserExitError(Exception):
    """When a premature exit from argparse is suppressed."""

    pass


class ReplArgparser(ArgumentParser):
    """Argparser that throws exception on bad arg instead of exiting."""

    def __init__(self, *args: Any, error_fmt: str = None, **kwargs: Any) -> None:
        """Add support for a custom argument for formatting errors."""
        super().__init__(*args, **kwargs)
        self.error_fmt = error_fmt or '{}'

    def exit(self, status=0, message=None):  # noqa A003
        """Stop argparse from exiting on bad options."""

        if status:
            raise ReplArgparserExitError(message)

    def error(self, message):
        """Raise an exception on bad arg instead of exiting."""
        raise ReplArgparserExitError(self.error_fmt.format(message))
