"""Handler for "help" REPL command."""

from __future__ import annotations

from argparse import Namespace

from .__common__ import ReplCommand


# ------------------------------------------------------------------------------
@ReplCommand.register('quit', 'q', history=False)
class Quit(ReplCommand):
    """Command help."""

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return r'q\[quit]', 'Quit.'

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Print help on all commands."""

        return False
