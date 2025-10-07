#!/usr/bin/env python3

"""Ollex CLI (See https://github.com/jin-gizmo/ollex)."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from ollex.commands import CliCommand
from ollex.version import __version__

__author__ = 'Murray Andrews'

PROG = Path(sys.argv[0]).stem


# ------------------------------------------------------------------------------
def process_cli_args() -> Namespace:
    """Process command line arguments."""

    argp = ArgumentParser(prog=PROG, description=__doc__)

    argp.add_argument(
        '-v', '--version', action='version', version=__version__, help='Show version and exit.'
    )

    # Add the sub-commonads
    subp = argp.add_subparsers(required=True)
    for cmd in sorted(CliCommand.commands.values(), key=lambda c: c.name):
        cmd(subp).add_arguments()

    args = argp.parse_args()

    try:
        args.handler.check_arguments(args)
    except ValueError as e:
        argp.error(str(e))

    return args


# ------------------------------------------------------------------------------
def main() -> int:
    """Show time."""
    try:
        args = process_cli_args()
        args.handler.execute(args)
        return 0
    except Exception as ex:
        # Uncomment for debugging
        # raise  # noqa: ERA001
        print(f'{PROG}: {ex}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(f'{PROG}: Interrupt', file=sys.stderr)
        return 2


# ------------------------------------------------------------------------------
# This only gets used during dev/test. Once deployed as a package, main() gets
# imported and run directly.
if __name__ == '__main__':
    exit(main())
