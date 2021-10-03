#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla hatch-all` command.
"""
import sys
from typing import Dict, List

import click

from hopla.hoplalib.hatchery.eggmodels import EggCollection
from hopla.hoplalib.hatchery.hatchalgorithms import HatchPlan, HatchPlanMaker
from hopla.hoplalib.hatchery.hatchcontroller import HatchRequester
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchPotionCollection
from hopla.hoplalib.throttling import ApiRequestThrottler
from hopla.hoplalib.user.usercontroller import HabiticaUserRequest
from hopla.hoplalib.user.usermodels import HabiticaUser
from hopla.hoplalib.zoo.foodmodels import FeedStatus
from hopla.hoplalib.zoo.petmodels import Pet


@click.command()
def hatch_all():
    """Hatch all the available eggs.

    \b
    hopla hatch-all - Print the possible hatchings, and, if the user
                      confirms, hatch all the available eggs
                      with all the available hatching potions.

    \b
    Examples:
    ----
    $ hopla hatch-all
    > A Treeling egg will be hatched by a Zombie potion.
    > A Robot egg will be hatched by a Desert potion.
    > Do you wish to proceed? [y/N]: yes
    Successfully hatched a Treeling-Zombie.
    Successfully hatched a Robot-Desert.

    """
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    eggs = EggCollection(user.get_eggs())
    potions = HatchPotionCollection(user.get_hatch_potions())
    pets: List[Pet] = to_pet_list(user.get_pets())

    plan_maker = HatchPlanMaker(
        egg_collection=eggs, hatch_potion_collection=potions, pets=pets
    )
    plan: HatchPlan = plan_maker.make_plan()

    if plan.is_empty():
        click.echo("The hatch plan is empty. Do you have enough pets and hatching potions?")
        click.echo("Exiting")
        sys.exit(1)

    plan_text: str = plan.format_plan()
    user_confirmed: bool = click.confirm(text=plan_text + "Do you wish to proceed?")
    if user_confirmed is True:
        _hatch_eggs(plan)
    else:
        click.echo("No eggs were hatched.")


def _hatch_eggs(plan: HatchPlan) -> None:
    """Hatch all the eggs. Print the result to the terminal.
    Warning: this function does not ask for confirmation.
    """
    throttler = ApiRequestThrottler(api_requests=[
        HatchRequester(item.egg.name, item.potion.name).post_hatch_egg for item in plan
    ])

    for hatch_request in throttler.release():
        response_msg: str = hatch_request()
        click.echo(response_msg)


def to_pet_list(pets: Dict[str, int]) -> List[Pet]:
    """Helper method that takes a pet_dict and returns a List[Pet]."""
    return [
        Pet(name, feed_status=FeedStatus(n)) for (name, n) in pets.items()
    ]
