"""Handler for "unset" REPL command."""

from __future__ import annotations

from argparse import Namespace
from contextlib import suppress

from rich.box import HORIZONTALS
from rich.table import Table

from ollex.lib.model import LLM_OPTIONS
from .__common__ import ReplCommand, Style


# ------------------------------------------------------------------------------
@ReplCommand.register('unset', 'u')
class UnsetLlm(ReplCommand):
    """Show / unset LLM options."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(dest='options', nargs='*')

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return (
            fr'u\[nset] [[{Style.arg}]OPTION[/{Style.arg}] ...]',
            'Show / unset the current (non-default) LLM options (* = clear all).',
        )

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Unset LLM model options."""

        for option in args.options:
            match option:
                case '*':
                    self.repl_context.llm_options = {}
                case _:
                    with suppress(KeyError):
                        del self.repl_context.llm_options[option]

        table = Table(box=HORIZONTALS)
        table.add_column('Option')
        table.add_column('Value', justify='right')
        for option in sorted(LLM_OPTIONS):
            table.add_row(option, str(self.repl_context.llm_options.get(option, '')))

        self.print(table)

        return True
