#!/usr/bin/env python3
import click

import logging
from hopla.hoplalib.Authorization import AuthorizationHandler

log = logging.getLogger()


# TODO: --browser option
@click.command()
def auth():
    """Authorize yourself to access the Habitica.com API

    hopla auth allows you interactively providing access credentials.
    """
    log.debug("function: hopla auth")
    auth_handler = AuthorizationHandler()
    auth_handler.set_hopla_credentials(overwrite=True)
