"""Interactive command handling for the REPL."""

from __future__ import annotations

import shlex
from abc import ABC, abstractmethod
from argparse import Namespace
from collections.abc import Callable
from readline import get_current_history_length, remove_history_item

from rich.console import Console

from ollex.lib.argparse import ReplArgparser

# Rich styles
Style = Namespace(
    arg='underline',  # Used for command arguments in help text.
    active='green',  # Used to indicate active item in a list
    prompt='italic',  # Used to print prompts
)


# ------------------------------------------------------------------------------
class ReplCommandError(Exception):
    """Raised when a REPL command fails."""

    pass


# ------------------------------------------------------------------------------
class ReplCommand(ABC):
    """Repl command handler."""

    commands: dict[str, type[ReplCommand]] = {}
    aliases: dict[str, str] = {}
    name = None  # Set by @register decorator for subclasses.
    help_ = None  # Set by @register from first line of docstring.
    add_to_history = True

    # --------------------------------------------------------------------------
    @classmethod
    def register(cls, name: str, *aliases: str, history: bool = True) -> Callable:
        """
        Register a REPL command handler class.

        :param name:    The name of the REPL command. Usually a long form.
        :param aliases: Aliases for the command. Usually short forms.
        :param history: Whether invocations of the command are added to command
                        history.

        This is a decorator. Usage is:

        .. code-block:: python

            @ReplCommand.register('my_command')
            class MyCommand(ReplCommand):
                ...
        """

        def decorate(cmd: type[ReplCommand]):
            """Register the command handler class."""
            cmd.name = name
            cls.commands[name] = cmd
            # A command is an alias for itself
            cls.aliases[name] = name
            for alias in aliases:
                cls.aliases[alias] = name
            cmd.add_to_history = history

            return cmd

        return decorate

    # --------------------------------------------------------------------------
    def __init__(self, repl_context: Namespace, console: Console, cmd_escape: str) -> None:
        """
        Initialize the command handler.

        :param repl_context:    A namespace containing context information for the
                                REPL that can be manipulated by commands.
        :param console:         A console for command output.
        :param cmd_escape:      A string to introduce commands.
        """

        self.repl_context = repl_context
        self.console = console
        self.cmd_escape = cmd_escape
        self.argp = ReplArgparser(add_help=False, error_fmt=f'Error: {{}} ({cmd_escape}h for help)')
        self.add_arguments()

    # --------------------------------------------------------------------------
    def print(self, *args, **kwargs):
        """Shortcut for printing to rich console."""

        # Disable rich random highlighting unless explicitly requested
        self.console.print(*args, **({'highlight': False} | kwargs))

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:  # noqa B027
        """Add the REPL command handler arguments (if any)."""
        pass

    # --------------------------------------------------------------------------
    @abstractmethod
    def execute(self, args: Namespace) -> bool:
        """
        Execute the REPL command with the specified arguments.

        :param args: Parsed arguments to pass to the REPL command.

        :return: True if the main REPL loop should continue, False otherwise.
        """

        raise NotImplementedError('execute')

    # --------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def help() -> tuple[str, str]:
        """
        Provide help information for the REPL command.

        :return:    A tuple (usage, description). Each may contain rich style
                    markup.
        """

        raise NotImplementedError('help')


# ------------------------------------------------------------------------------
class ReplCommandController:
    """Controller / dispatcher for REPL commands."""

    # --------------------------------------------------------------------------
    def __init__(self, repl_context: Namespace, console: Console, cmd_escape: str) -> None:
        """
        Initialize the REPL command controller.

        :param repl_context:    A namespace containing context information for the
                                REPL that can be manipulated by commands.
        :param console:         A console for command output.
        :param cmd_escape:      A string to introduce commands.
        """

        self.repl_context = repl_context
        self.console = console
        self.cmd_escape = cmd_escape
        self.command_handlers = {
            k: v(repl_context, console, cmd_escape) for k, v in ReplCommand.commands.items()
        }

    # --------------------------------------------------------------------------
    def do_cmd(self, command: str) -> bool:
        """
        Execute the REPL command with the specified arguments.

        :param command: A shell style command to execute via one of the REPL commands.

        """

        argv = shlex.split(command.removeprefix(self.cmd_escape))
        if not argv:
            raise ReplCommandError('No command specified')

        try:
            handler = self.command_handlers[ReplCommand.aliases[argv[0]]]
        except KeyError:
            remove_history_item(get_current_history_length() - 1)
            raise ReplCommandError(f'{argv[0]}: No such command (try {self.cmd_escape}help)')

        if not handler.add_to_history:
            remove_history_item(get_current_history_length() - 1)

        args = handler.argp.parse_args(argv[1:])
        return handler.execute(args)
