"""Handler for "coll" REPL command."""

from __future__ import annotations

from argparse import Namespace
from typing import Any

from rich.box import HORIZONTALS
from rich.table import Table

from .__common__ import ReplCommand, ReplCommandError, Style


# ------------------------------------------------------------------------------
@ReplCommand.register('coll', 'c')
class SetCollection(ReplCommand):
    """Set the database collection to be used."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('collection', nargs='*')

    # --------------------------------------------------------------------------
    @staticmethod
    def help() -> tuple[str, str]:
        """Command help."""

        return (
            fr'c\[oll] [[{Style.arg}]COLLECTION ...]',
            'Show the collections in use or set to the ones specified.',
        )

    # --------------------------------------------------------------------------
    def execute(self, args: Namespace) -> bool:
        """Set the LLM model."""

        def highlight_if(active: bool, v: Any) -> str:
            """Highlight a value using rich markup if it's active."""
            return f'[{Style.active}]{v}[/{Style.active}]' if active else str(v)

        collection_info: dict[str, dict[str, Any]] = self.repl_context.collection_info

        if args.collection:
            # Validate that we have the collections being requested.
            requested_collections = set(args.collection)
            available_collections = collection_info.keys()
            if unavaible_collections := requested_collections - available_collections:
                raise ReplCommandError(
                    f'Unavailable collections: {", ".join(sorted(unavaible_collections))}'
                )
            self.repl_context.collections = sorted(requested_collections)
            self.print(f'Collection(s) set to {", ".join(self.repl_context.collections)}')
            return True

        # Just show which collections are available in a table.
        columns = set()
        for c_info in collection_info.values():
            columns |= c_info.keys()
        # There are some columns we don't want to show
        columns = sorted(columns - {'files'})

        current_collections = set(getattr(self.repl_context, 'collections', []))
        table = Table(box=HORIZONTALS)
        table.add_column()  # Current collection indicator
        table.add_column('Name')
        for col in columns:
            table.add_column(col.replace('_', '\n').title())
        for c_name, c_info in sorted(collection_info.items()):
            active_row = c_name in current_collections
            table.add_row(
                highlight_if(active_row, '*') if active_row else '',
                highlight_if(active_row, c_name),
                *(highlight_if(active_row, c_info.get(k, '')) for k in columns),
            )

        self.print(table)
        return True
