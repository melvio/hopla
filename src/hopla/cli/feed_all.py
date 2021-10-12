#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla feed-all` command.
"""
import logging
import sys
from typing import Any, Callable, Dict, Iterator, List, NoReturn, Optional, Union

import click
from requests import Response

from hopla.hoplalib import hopla_option
from hopla.cli.groupcmds.get_user import HabiticaUser, HabiticaUserRequest
from hopla.hoplalib.throttling import RateLimitingAwareThrottler
from hopla.hoplalib.zoo.foodmodels import FoodStockpile, FoodStockpileBuilder
from hopla.hoplalib.zoo.petcontroller import FeedPostRequester
from hopla.hoplalib.zoo.zoomodels import Zoo, ZooBuilder
from hopla.hoplalib.zoo.zoofeed_algorithms import FeedAlgorithm, FeedPlan

log = logging.getLogger()


def __get_feed_plan_or_exit() -> Union[NoReturn, FeedPlan]:
    """Get the user and build the feed plan"""
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    stockpile: FoodStockpile = FoodStockpileBuilder().user(user).build()
    zoo: Zoo = ZooBuilder(user).build()

    algorithm = FeedAlgorithm(zoo=zoo, stockpile=stockpile)
    return algorithm.make_plan()


def __confirm_with_user_or_abort(plan: FeedPlan) -> Optional[NoReturn]:
    """Ask the user to confirm the specified plan.

    :param plan: the feed plan to display
    :return: Don't return if the user wants to abort
    """

    prompt_msg = f"{plan.format_plan()}\nDo you want to proceed?"
    click.confirm(text=prompt_msg, abort=True)


def __feed_pets_without_confirmation(plan: FeedPlan):
    """Feed all the pets in the plan. Print the result to the terminal.

    Warning: this function does ask for confirmation.
    """
    # Feel free to refactor this such that we don't iterate over
    # the plan twice.
    feed_requests: List[Callable[[], Response]] = [
        FeedPostRequester.build_from(item).post_feed_request
        for item in plan
    ]
    throttler = RateLimitingAwareThrottler(feed_requests)
    feed_response_iter: Iterator[Response] = throttler.perform_and_yield_response()
    for item in plan:
        feed_response: Response = next(feed_response_iter)
        response_json: Dict[str, Any] = feed_response.json()
        if response_json["success"] is True:
            click.echo(response_json["message"])
        else:
            click.echo(f"Failed to feed {item.pet_name}\n"
                       f"{response_json['error']}: {response_json['message']}")


@click.command()
@hopla_option.no_interactive_option()
def feed_all(no_interactive: bool) -> None:
    """Feed all your pets.

    This command will first feed normal pets, then your quest pets, and
    finally all your pets that were hatched with magic hatching potions.

    Not this command will first show you the feed plan, and for safety,
    ask for your confirmation. Pets will only if you confirm this prompt.


    \b
    Examples
    --------
    # list the feeding plan, ask for confirmation, feed all pets if confirmed.
    $ hopla feed-all
    > Pet BearCub-Zombie will get 9 RottenMeat.
    > Pet Fox-CottonCandyBlue will get 9 CottonCandyBlue.
    > Do you want to proceed? [y/N]: yes


    \b
    # feed all the pets without asking for confirmation
    $ hopla feed-all --yes
    $ hopla feed-all --force

    \f
    :param no_interactive:
    """
    log.debug(f"hopla feed-all {no_interactive=}")
    plan: FeedPlan = __get_feed_plan_or_exit()
    if plan.isempty():
        click.echo(
            "The feed plan is empty. Reasons for this could be:\n"
            "1. There is insufficient food available to turn pets into mounts.\n"
            "2. You don't have any feedable pets."
        )
        sys.exit(0)

    if no_interactive is False:
        __confirm_with_user_or_abort(plan)

    __feed_pets_without_confirmation(plan)
