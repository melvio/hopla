#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla hatch` GROUP command.
"""

import sys
from typing import NoReturn

import click
import requests

from hopla.hoplalib.hatchery.hatchcontroller import HatchRequester


@click.group()
def hatch():
    """GROUP for hatching eggs."""


def hatch_egg(*, egg_name: str, potion_name: str) -> NoReturn:
    """
    Hatch an egg by performing an API request and echo the result to the
    terminal.
    """
    requester = HatchRequester(
        egg_name=egg_name,
        hatch_potion_name=potion_name
    )
    response: requests.Response = requester.post_hatch_egg_request()
    json: dict = response.json()
    if json["success"] is True:
        click.echo(f"Successfully hatched a {egg_name}-{potion_name}.")
        sys.exit(0)

    click.echo(f"{json['error']}: {json['message']}")
    sys.exit(1)
