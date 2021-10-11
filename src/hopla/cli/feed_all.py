#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla feed-all` command.
"""
import logging
import sys
from typing import Callable, List, NoReturn, Optional, Union

import click

from hopla.hoplalib import hopla_option
from hopla.cli.groupcmds.get_user import HabiticaUser, HabiticaUserRequest
from hopla.hoplalib.throttling import ApiRequestThrottler
from hopla.hoplalib.zoo.foodmodels import FoodStockpile, FoodStockpileBuilder
from hopla.hoplalib.zoo.petcontroller import FeedPostRequester
from hopla.hoplalib.zoo.zoomodels import Zoo, ZooBuilder
from hopla.hoplalib.zoo.zoofeed_algorithms import ZooFeedAlgorithm, ZookeeperFeedPlan

log = logging.getLogger()


def __get_feed_plan_or_exit() -> Union[NoReturn, ZookeeperFeedPlan]:
    """Get the user and build the zookeeper plan"""
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    stockpile: FoodStockpile = FoodStockpileBuilder().user(user).build()
    zoo: Zoo = ZooBuilder(user).build()

    algorithm = ZooFeedAlgorithm(zoo=zoo, stockpile=stockpile)
    return algorithm.make_plan()


def __confirm_with_user_or_abort(plan: ZookeeperFeedPlan) -> Optional[NoReturn]:
    """Ask the user to confirm the specified plan.

    :param plan: the zookeeper feed plan to display
    :return: Don't return if the user wants to abort
    """

    prompt_msg = f"{plan.format_plan()}\nDo you want to proceed?"
    click.confirm(text=prompt_msg, abort=True)


def feed_all_pets_and_exit(*, no_interactive: bool = False) -> NoReturn:
    """Feed all the pets"""
    plan: ZookeeperFeedPlan = __get_feed_plan_or_exit()
    if plan.isempty():
        click.echo(
            "The feed plan is empty. Reasons for this could be:\n"
            "1. There is insufficient food available to turn pets into mounts.\n"
            "2. You don't have any feedable pets."
        )
        sys.exit(0)

    if no_interactive is False:
        __confirm_with_user_or_abort(plan)

    feed_requests: List[Callable[[], None]] = []
    for item in plan:
        feed_requester: FeedPostRequester = FeedPostRequester.build_from(item)
        feed_requests.append(feed_requester.post_feed_request_get_data_or_exit)

    throttler = ApiRequestThrottler(feed_requests)
    throttler.execute_all_requests()
    sys.exit(0)


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
    feed_all_pets_and_exit(no_interactive=no_interactive)
