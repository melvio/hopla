"""
The module with CLI code that handles the `hopla add` group command.
"""
import logging

import click

log = logging.getLogger()


@click.group()
def add():
    """GROUP for adding things to Habitica."""
