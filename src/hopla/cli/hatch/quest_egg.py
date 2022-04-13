#!/usr/bin/env python3
"""
Module with code for the `hopla hatch quest-egg` command.
"""
import logging

import click

from hopla.cli.groupcmds.hatch import hatch_egg
from hopla.hoplalib.hatchery.egg_data import EggData
from hopla.hoplalib.hatchery.hatchpotion_data import HatchPotionData

log = logging.getLogger()


@click.command()
@click.argument(
    "egg_name", metavar="QUEST_EGG_NAME",
    type=click.Choice(EggData.quest_egg_names)
)
@click.argument(
    "potion_name",
    type=click.Choice(HatchPotionData.drop_hatch_potion_names)
)
def quest_egg(egg_name: str, potion_name: str):
    """hatch a quest egg.

    \b
    QUEST_EGG_NAME =
        Name of the quest egg. (e.g. Frog, Cow, Spider, TRex, Dolphin)
    \b
    POTION_NAME =
        Name of the potion. Must be a standard drop hatching potion.

    \b
    Examples
    -----
    # hatch a Monkey-Shade
    $ hopla hatch quest-egg Monkey Shade

    \b
    # hatch a Sabretooth-Base
    $ hopla hatch quest-egg Sabretooth Base

    """
    log.debug(f"hopla hatch quest-egg {egg_name=} {potion_name=}")

    hatch_egg(egg_name=egg_name, potion_name=potion_name)
