"""Handler for "results" REPL command."""

from __future__ import annotations

from argparse import Namespace

from .__common__ import ReplCommand, ReplCommandError, Style


# ------------------------------------------------------------------------------
@ReplCommand.register('results', 'r')
class SetNumberOfSearchResults(ReplCommand):
    """Set the number of search results from the database to feed to the LLM."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('n_results', nargs='?')

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return (
            fr'r\[esults] [[{Style.arg}]N]',
            'Set the number of search results from the database to feed to the LLM.',
        )

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Set the number of search results from the database to feed to the LLM."""

        if args.n_results is None:
            self.print(f'Number of search results = {self.repl_context.search_results}')
            return True

        try:
            n_results = int(args.n_results)
        except ValueError as e:
            raise ReplCommandError(f'{args.n_results}: {e}')

        if n_results <= 0:
            raise ReplCommandError('Number of search results must be > 0')

        self.repl_context.search_results = n_results
        self.print(f'Number of search results set to {n_results}')
        return True
