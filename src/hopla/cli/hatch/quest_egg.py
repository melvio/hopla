#!/usr/bin/env python3
"""
Module with code for the `hopla hatch quest-egg` command.
"""
import click

from hopla.hoplalib.hatchery.hatchdata import EggData, HatchingPotionData


@click.command()
@click.argument("egg_name",
                type=click.Choice(EggData.quest_egg_names))
@click.argument("potion_name",
                type=click.Choice(sorted(HatchingPotionData.drop_hatching_potion_names)))
def quest_egg(egg_name: str, potion_name: str):
    """hatch a quest egg.
    To be implemented in: https://github.com/melvio/hopla/issues/170
    """
    raise NotImplementedError("hopla hatch quest-egg")
