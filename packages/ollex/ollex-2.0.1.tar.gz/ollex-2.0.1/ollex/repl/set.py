"""Handler for "set" REPL command."""

from __future__ import annotations

from argparse import Namespace

from rich.box import HORIZONTALS
from rich.table import Table

from ollex.lib.argparse import StoreNameValuePair
from ollex.lib.model import LLM_OPTIONS
from .__common__ import ReplCommand, ReplCommandError, Style


# ------------------------------------------------------------------------------
@ReplCommand.register('set', 's')
class SetLlm(ReplCommand):
    """Show / set LLM options."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(dest='options', action=StoreNameValuePair, nargs='*')

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return (
            fr's\[et] [[{Style.arg}]OPTION[/{Style.arg}]=[{Style.arg}]VALUE[/{Style.arg}]]',
            'Show / set the current (non-default) LLM options.',
        )

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Set LLM model options."""

        if args.options:
            for option, value in args.options.items():
                try:
                    # Cast the value to correct type
                    self.repl_context.llm_options[option] = LLM_OPTIONS[option](value)
                except KeyError:
                    raise ReplCommandError(f'{option}: Unknown option')
                except Exception as e:
                    raise ReplCommandError(f'{option}: {e}')

        table = Table(box=HORIZONTALS)
        table.add_column('Option')
        table.add_column('Value', justify='right')
        for option in sorted(LLM_OPTIONS):
            table.add_row(option, str(self.repl_context.llm_options.get(option, '')))

        self.print(table)

        return True
