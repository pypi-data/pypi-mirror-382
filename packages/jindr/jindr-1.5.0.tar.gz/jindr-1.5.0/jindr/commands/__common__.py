"""Common components for docma CLI commands."""

from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import Namespace
from collections.abc import Callable

from jindr.exceptions import JinDrInternalError

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
class CliCommand(ABC):
    """ClI command handler."""

    commands: dict[str, type[CliCommand]] = {}
    name = None  # Set by @register decorator for subclasses.
    help_ = None  # Set by @register from first line of docstring.
    aliases = None  # Set by @register decorator for subclasses.

    # --------------------------------------------------------------------------
    @classmethod
    def register(cls, name: str, *aliases) -> Callable:
        """
        Register a CLI command handler class.

        This is a decorator. Usage is:

        .. code-block:: python

            @CliCommand.register('my_command', [aliases...])
            class MyCommand(CliCommand):
                ...

        The help for the command is taken from the first line of the docstring.
        """

        def decorate(cmd: type[CliCommand]):
            """Register the command handler class."""
            cmd.name = name
            cmd.aliases = aliases or []
            try:
                cmd.help_ = cmd.__doc__.splitlines()[0]
            except (AttributeError, IndexError):
                raise JinDrInternalError(f'Class {cmd.__name__} must have a docstring')
            cls.commands[name] = cmd
            return cmd

        return decorate

    # --------------------------------------------------------------------------
    def __init__(self, subparser):
        """Initialize the command handler."""
        self.argp = subparser.add_parser(
            self.name, aliases=self.aliases, help=self.help_, description=self.help_
        )
        self.argp.set_defaults(handler=self)

    # --------------------------------------------------------------------------
    def add_arguments(self):  # noqa B027
        """Add arguments to the command handler."""
        pass

    # --------------------------------------------------------------------------
    @staticmethod  # noqa B027
    def check_arguments(args: Namespace):
        """
        Validate arguments.

        :param args:        The namespace containing the arguments.
        :raise ValueError:  If the arguments are invalid.
        """

        pass

    # --------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def execute(args: Namespace) -> int:
        """
        Execute the CLI command with the specified arguments.

        :return:    Exit status.
        """
        raise NotImplementedError('execute')
