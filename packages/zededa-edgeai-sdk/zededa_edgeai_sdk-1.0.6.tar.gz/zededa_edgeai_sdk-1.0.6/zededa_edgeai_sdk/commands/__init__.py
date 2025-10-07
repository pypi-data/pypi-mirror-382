"""Command registry and discovery system for the CLI.

Provides the plugin-like command system that automatically discovers
and registers available CLI sub-commands.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional


@dataclass
class CommandSpec:
    """Specification for a CLI sub-command containing metadata and registration logic.
    
    This dataclass defines the structure for CLI commands, holding the command name,
    help text, and a registration function that configures argparse options.
    """

    name: str
    help: str
    register: Callable[[argparse._SubParsersAction], None]


def _load_builtin_commands() -> List[CommandSpec]:
    """Import and return all built-in command specifications.
    
    This function dynamically imports command modules and collects their
    CommandSpec objects for registration with the CLI system.
    """
    from .login import LOGIN_COMMAND
    from .catalogs import CATALOGS_COMMAND
    from .logout import LOGOUT_COMMAND
    from .set_catalog_context import SET_CATALOG_CONTEXT_COMMAND

    return [LOGIN_COMMAND, CATALOGS_COMMAND, LOGOUT_COMMAND, SET_CATALOG_CONTEXT_COMMAND]


def iter_commands() -> Iterable[CommandSpec]:
    """Iterate through all available CLI commands.
    
    Yields CommandSpec objects for each registered command, providing
    a centralized way to access all available CLI functionality.
    """

    yield from _load_builtin_commands()


def get_command(name: str) -> Optional[CommandSpec]:
    """Retrieve a specific command by name.
    
    Searches through all registered commands and returns the CommandSpec
    matching the provided name, or None if no command is found.
    """
    for command in iter_commands():
        if command.name == name:
            return command
    return None


def register_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register all commands with the argparse subparser system.
    
    Iterates through available commands and calls their register function
    to configure argparse with the appropriate sub-commands and options.
    """
    for command in iter_commands():
        command.register(subparsers)
