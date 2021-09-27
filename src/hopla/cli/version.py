"""
The module with CLI code that handles the `hopla version` command.
"""

import logging

import click

from hopla.hoplalib.hoplaversion import HoplaVersion

log = logging.getLogger()


@click.command()
def version():
    """Print the Hopla version string.

    \f
    :return:
    """
    log.debug("hopla version")
    click.echo(HoplaVersion().semantic_version())
