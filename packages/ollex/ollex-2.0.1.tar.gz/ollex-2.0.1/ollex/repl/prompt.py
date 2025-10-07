"""Handler for "prompt" REPL command."""

from __future__ import annotations

from argparse import Namespace

from .__common__ import ReplCommand, ReplCommandError, Style


# ------------------------------------------------------------------------------
@ReplCommand.register('prompt', 'p')
class Prompt(ReplCommand):
    """Show info on prompts."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('prompt_id', nargs='?')

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return (
            fr'p\[rompt] [[{Style.arg}]ID]',
            'Show the prompt IDs in use or show the content of the one specified.',
        )

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Show info on prompts."""

        if args.prompt_id:
            try:
                self.print(f'[{Style.prompt}]{self.repl_context.prompts[args.prompt_id]}')
            except KeyError:
                raise ReplCommandError('Invalid prompt ID')
            return True

        self.print('[bold]Prompts are:')
        for prompt_id in self.repl_context.prompts:
            self.print(f'    {prompt_id}')
        return True
