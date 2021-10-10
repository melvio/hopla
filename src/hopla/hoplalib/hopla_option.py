#!/usr/bin/env python3
"""
Module with common click options and arguments.
"""
import click


def no_interactive_option() -> click.option:
    """A decorator to handle --force consistently throughout hopla."""
    return click.option(
        "--force", "--yes", "-f", "no_interactive",
        is_flag=True, default=False, show_default=True,
        help="Don't ask for confirmation before executing this command."
    )
