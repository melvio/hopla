#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla hatch standard-egg` command.
"""
import logging
import sys

import click
import requests

from hopla.hoplalib.hatchery.hatchcontroller import HatchRequester
from hopla.hoplalib.hatchery.hatchdata import EggData, HatchingPotionData

log = logging.getLogger()


@click.command()
@click.argument("egg_name", metavar="STANDARD_EGG_NAME",
                type=click.Choice(EggData.drop_egg_names))
@click.argument("potion_name", metavar="POTION_NAME",
                type=click.Choice(HatchingPotionData.hatching_potion_names))
def standard_egg(egg_name: str, potion_name: str) -> None:
    """Hatch a standard egg.

    \b
    STANDARD_EGG_NAME =
        Name of the standard egg. Must be one of: BearCub, Cactus, Dragon,
        FlyingPig, Fox, LionCub, PandaCub, TigerCub, Wolf
    \b
    POTION_NAME =
        Name of potion name. (e.g. White, Desert, Sunset, Windup)

    \b
    Examples
    -----
    # hatch a Wolf-Shade
    $ hopla hatch standard-egg Wolf Shade


    \f
    [APIDOCS](https://habitica.com/apidoc/#api-User-UserHatch)
    :param egg_name:
    :param potion_name:
    :return:
    """
    log.debug(f"hopla hatch standard-egg {egg_name=} {potion_name=}")

    requester = HatchRequester(
        egg_name=egg_name,
        hatching_potion_name=potion_name
    )

    response: requests.Response = requester.post_hatch_egg()
    json: dict = response.json()
    if json["success"]:
        click.echo(f"Successfully hatched a {egg_name}-{potion_name}.")
    else:
        click.echo(f"{json['error']}: {json['message']}")
        sys.exit(1)
