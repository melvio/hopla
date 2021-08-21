#!/usr/bin/env python3
import click

import logging
from hopla.hoplalib.Authorization import AuthorizationHandler

log = logging.getLogger()


# TODO: --browser option
@click.command()
def auth():
    log.debug("function: hopla auth")
    auth_hander = AuthorizationHandler()
    auth_hander.set_hopla_credentials(overwrite=True)
