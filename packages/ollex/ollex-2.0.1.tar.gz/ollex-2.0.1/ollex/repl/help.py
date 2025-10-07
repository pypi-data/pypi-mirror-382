"""Handler for "help" REPL command."""

from __future__ import annotations

from argparse import Namespace

from rich.box import HORIZONTALS
from rich.table import Table

from .__common__ import ReplCommand


# ------------------------------------------------------------------------------
@ReplCommand.register('help', 'h', '?', history=False)
class Help(ReplCommand):
    """Command help."""

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return r'h\[elp]', 'Show this help message.'

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Print help on all commands."""

        table = Table(show_header=True, leading=1, box=HORIZONTALS)
        table.add_column('Command', no_wrap=True, vertical='top')
        table.add_column('Description', vertical='top')
        for _, handler in sorted(ReplCommand.commands.items()):
            table.add_row(*handler.help())
        self.print(table)
        self.print()
        self.print(fr'Run commands as {self.cmd_escape}cmd \[options]')

        return True
