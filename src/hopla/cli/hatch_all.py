#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla hatch-all` command.
"""
import logging
import sys
from typing import Any, Callable, Dict, Iterator, List

import click
from requests import Response

from hopla.hoplalib import hopla_option
from hopla.hoplalib.hatchery.eggmodels import EggCollection
from hopla.hoplalib.hatchery.hatchalgorithms import HatchPlan, HatchPlanMaker
from hopla.hoplalib.hatchery.hatchcontroller import HatchRequester
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchPotionCollection
from hopla.hoplalib.throttling import RateLimitingAwareThrottler
from hopla.hoplalib.user.usercontroller import HabiticaUserRequest
from hopla.hoplalib.user.usermodels import HabiticaUser
from hopla.hoplalib.zoo.foodmodels import FeedStatus
from hopla.hoplalib.zoo.petmodels import Pet

log = logging.getLogger()


@click.command()
@hopla_option.no_interactive_option()
def hatch_all(no_interactive: bool) -> None:
    """Hatch all the available eggs.

    \b
    hopla hatch-all - Print the possible hatchings, and, if the user
                      confirms, hatch all the available eggs
                      with all the available hatching potions.

    \b
    Examples:
    ----
    # Show hatching list, ask for confirmation, optionally hatch eggs.
    $ hopla hatch-all
    > A Treeling egg will be hatched by a Zombie potion.
    > A Robot egg will be hatched by a Desert potion.
    > Do you wish to proceed? [y/N]: yes
    Successfully hatched a Treeling-Zombie.
    Successfully hatched a Robot-Desert.

    \b
    # Hatch all available eggs without asking for confirmation.
    $ hopla hatch-all --yes
    Successfully hatched a Treeling-Zombie.
    Successfully hatched a Robot-Desert.

    """
    log.debug(f"hopla hatch-all {no_interactive=}")
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    eggs = EggCollection(user.get_eggs())
    potions = HatchPotionCollection(user.get_hatch_potions())
    pets: List[Pet] = to_pet_list(user.get_pets())

    plan_maker = HatchPlanMaker(
        egg_collection=eggs, hatch_potion_collection=potions, pets=pets
    )
    plan: HatchPlan = plan_maker.make_plan()

    if plan.is_empty():
        click.echo(
            "The hatch plan is empty. Do you have enough eggs and hatching potions?\n"
            "Exiting"
        )
        sys.exit(1)

    if no_interactive is True:
        _hatch_eggs_without_confirmation(plan)
    else:
        _ask_for_confirmation_and_maybe_hatch(plan)


def _ask_for_confirmation_and_maybe_hatch(plan: HatchPlan) -> None:
    plan_text: str = plan.format_plan()
    user_confirmed: bool = click.confirm(text=plan_text + "Do you wish to proceed?")
    if user_confirmed is True:
        _hatch_eggs_without_confirmation(plan)
    else:
        click.echo("No eggs were hatched.")


def _hatch_eggs_without_confirmation(plan: HatchPlan) -> None:
    """Hatch all the eggs. Print the result to the terminal.
    Warning: this function does not ask for confirmation.
    """
    # Feel free to refactor this such that we don't iterate over
    # the plan twice.
    api_requests: List[Callable[[], Response]] = [
        HatchRequester(item.egg.name, item.potion.name).post_hatch_egg_request for item in plan
    ]

    throttler = RateLimitingAwareThrottler(api_requests)
    api_responses: Iterator[Response] = throttler.perform_and_yield_response()
    for item in plan:
        response: Response = next(api_responses)
        response_json: Dict[str, Any] = response.json()
        pet_name = f"{item.egg.name}-{item.potion.name}"
        if response_json["success"] is True:
            click.echo(f"Successfully hatched a {pet_name}.")
        else:
            click.echo(f"Failed to hatch {pet_name}:\n"
                       f"{response_json['error']}: {response_json['message']}")


def to_pet_list(pets: Dict[str, int]) -> List[Pet]:
    """Helper method that takes a pet_dict and returns a List[Pet]."""
    return [
        Pet(name, feed_status=FeedStatus(n)) for (name, n) in pets.items()
    ]
