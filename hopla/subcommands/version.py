#!/usr/bin/env python3
import click

import logging

log = logging.getLogger()


@click.command()
def version():
    """print hopla's version string

    \f
    :return:
    """
    log.debug("function: hopla version")
    click.echo("v0.0.1-beta-release")
