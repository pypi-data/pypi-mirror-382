"""Handler for "set" REPL command."""

from __future__ import annotations

from argparse import Namespace
from readline import get_current_history_length, get_history_item

from rich.table import Table

from .__common__ import ReplCommand


# ------------------------------------------------------------------------------
@ReplCommand.register('history', 'hi', history=False)
class CommandHistory(ReplCommand):
    """Show command history.."""

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return r'hi\[story]', 'Show command history.'

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Set LLM model options."""

        table = Table(box=None, show_header=False)
        table.add_column('#', justify='right')
        table.add_column('Command')
        for n in range(1, get_current_history_length() + 1):
            table.add_row(str(n), get_history_item(n))
        self.print(table)

        return True
