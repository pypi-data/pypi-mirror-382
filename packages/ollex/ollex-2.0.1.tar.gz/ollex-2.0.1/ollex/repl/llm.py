"""Handler for "llm" REPL command."""

from __future__ import annotations

from argparse import Namespace

import ollama

from .__common__ import ReplCommand, ReplCommandError, Style


# ------------------------------------------------------------------------------
@ReplCommand.register('llm', 'l')
class SetLlm(ReplCommand):
    """Set the LLM model to be used."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('llm', nargs='*')

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return (
            fr'l\[lm] [[{Style.arg}]MODEL ...]',
            'Show the LLMs in use or set to the ones specified.',
        )

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Set the LLM model."""

        available_llms = {m.model.removesuffix(':latest') for m in ollama.list().models}

        if args.llm:
            # Update current LLM settings
            requested_llms = {m.removesuffix(':latest') for m in args.llm}
            if unavailable_llms := requested_llms - available_llms:
                raise ReplCommandError(f'Unavailable models: {", ".join(sorted(unavailable_llms))}')
            self.repl_context.llm = sorted(requested_llms)
            self.print(f'LLM(s) set to {", ".join(self.repl_context.llm)}')
            return True

        # Just report current setting
        try:
            current_llms = set(self.repl_context.llm)
        except AttributeError:
            current_llms = set()

        self.print('[bold]Available LLMs (* = selected):')
        for llm in sorted(available_llms):
            self.print(f'[{Style.active}]  * {llm}' if llm in current_llms else f'    {llm}')
        return True
