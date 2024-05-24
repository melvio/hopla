#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla hatch` command.
"""

import sys
from typing import NoReturn

import click
import requests

from hopla.hoplalib.hatchery.egg_data import EggData
from hopla.hoplalib.hatchery.hatchcontroller import HatchRequester
from hopla.hoplalib.hatchery.hatchpotion_data import HatchPotionData


@click.command()
@click.argument(
    "egg_name",
    type=click.Choice(sorted(EggData.egg_names))
)
@click.argument(
    "potion_name",
    type=click.Choice(sorted(HatchPotionData.hatch_potion_names))
)
def hatch(*, egg_name: str, potion_name: str) -> NoReturn:
    """CMD for hatching an egg

    \b
    EGG_NAME =
    Name of the quest egg. (e.g. Frog, Cow, Spider, TRex, Dolphin, PandaCub, TigerCub, Wolf)

    \b
    POTION_NAME =
    Name of the potion. Must be a hatching potion.

    \b
    Examples
    -----
    # hatch a Monkey-Shade
    $ hopla hatch Monkey Shade

    \b
    # hatch a Sabretooth-Base
    $ hopla hatch Sabretooth Base

    \b
    # hatch a Wolf-Shade
    $ hopla hatch standard-egg Wolf Shade

    \b
    # hatch a Fox-SolarSystem
    $ hopla hatch standard-egg Fox SolarSystem
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
