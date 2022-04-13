#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla hatch standard-egg` command.
"""
import logging
from typing import NoReturn

import click

from hopla.cli.groupcmds.hatch import hatch_egg
from hopla.hoplalib.hatchery.egg_data import EggData
from hopla.hoplalib.hatchery.hatchpotion_data import HatchPotionData

log = logging.getLogger()


@click.command()
@click.argument(
    "egg_name", metavar="STANDARD_EGG_NAME",
    type=click.Choice(EggData.drop_egg_names)
)
@click.argument(
    "potion_name", metavar="POTION_NAME",
    type=click.Choice(sorted(HatchPotionData.hatch_potion_names))
)
def standard_egg(egg_name: str, potion_name: str) -> NoReturn:
    """Hatch a standard egg.

    \b
    STANDARD_EGG_NAME =
        Name of the standard egg. Must be one of: BearCub, Cactus, Dragon,
        FlyingPig, Fox, LionCub, PandaCub, TigerCub, Wolf
    \b
    POTION_NAME =
        Name of the hatching potion. (e.g. White, Desert, Sunset, Windup)

    \b
    Examples
    -----
    # hatch a Wolf-Shade
    $ hopla hatch standard-egg Wolf Shade

    \b
    # hatch a Fox-SolarSystem
    $ hopla hatch standard-egg Fox SolarSystem

    \f
    [APIDOCS](https://habitica.com/apidoc/#api-User-UserHatch)
    :param egg_name:
    :param potion_name:
    :return:
    """
    log.debug(f"hopla hatch standard-egg {egg_name=} {potion_name=}")

    hatch_egg(egg_name=egg_name, potion_name=potion_name)
