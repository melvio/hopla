#!/usr/bin/env python3
"""
Module with common click options and arguments.
"""
from typing import Final, List

import click

NO_INTERACTION_OPTION_NAMES: Final[List[str]] = ["--force", "--yes", "-f"]


def no_interactive_option() -> click.option:
    """A decorator to handle --force consistently throughout hopla."""
    return click.option(
        *NO_INTERACTION_OPTION_NAMES, "no_interactive",
        is_flag=True, default=False, show_default=True,
        help="Don't ask for confirmation before executing this command."
    )
