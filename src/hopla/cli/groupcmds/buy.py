"""
The module with CLI code that handles the `hopla buy` group command.
"""

import click


@click.group()
def buy():
    """
    GROUP to buy things.
    """
