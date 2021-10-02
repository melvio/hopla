#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla hatch` GROUP command.
"""

import click


@click.group()
def hatch():
    """GROUP for hatching eggs."""
