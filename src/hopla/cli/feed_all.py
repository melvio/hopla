#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla feed-all` command.
"""
import logging
import sys
from typing import NoReturn, Optional, Union

import click
import requests

from hopla.cli.groupcmds.get_user import HabiticaUser, HabiticaUserRequest
from hopla.hoplalib.zoo.feeding_clickhelper import get_feed_data_or_exit
from hopla.hoplalib.zoo.foodmodels import FoodStockpile, FoodStockpileBuilder
from hopla.hoplalib.zoo.petcontroller import FeedPostRequester
from hopla.hoplalib.zoo.petmodels import Zoo, ZooBuilder
from hopla.hoplalib.zoo.zoofeeding_algorithms import ZooFeedingAlgorithm, ZookeeperFeedPlan

log = logging.getLogger()


def __get_feeding_plan_or_exit() -> Union[NoReturn, ZookeeperFeedPlan]:
    """Get the user and build the zookeeper plan"""
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    stockpile: FoodStockpile = FoodStockpileBuilder().user(user).build()
    zoo: Zoo = ZooBuilder(user).build()

    algorithm = ZooFeedingAlgorithm(zoo=zoo, stockpile=stockpile)
    return algorithm.make_plan()


def __confirm_with_user_or_abort(plan: ZookeeperFeedPlan) -> Optional[NoReturn]:
    """Ask the user to confirm the specified plan.

    :param plan: the zookeeper feeding plan to display
    :return: Don't return if the user wants to abort
    """

    prompt_msg = f"{plan.format_plan()}Do you want to proceed?"
    click.confirm(text=prompt_msg, abort=True)


def feed_all_pets_and_exit() -> NoReturn:
    """Feed all the pets"""
    plan: ZookeeperFeedPlan = __get_feeding_plan_or_exit()
    if plan.isempty():
        click.echo(
            "The feed plan is empty. Reasons could include:\n"
            "1. There is insufficient food available to turn pets into mounts\n"
            "2. You don't have any feedable pets."
        )
        sys.exit(0)

    __confirm_with_user_or_abort(plan)

    for item in plan:
        request = FeedPostRequester(pet_name=item.pet_name,
                                    food_name=item.food_name,
                                    food_amount=item.times)
        response: requests.Response = request.post_feed_request()
        get_feed_data_or_exit(feed_response=response)
    sys.exit(0)


@click.command()
def feed_all():
    """Feed all your pets.

    This command will first feed normal pets, then your quest pets, and
    finally all your pets that were hatched with magic hatching potions.

    Not this command will first show you the feeding plan, and for safety,
    ask for your confirmation. Pets will only if you confirm this prompt.
    """
    log.debug("hopla feed-all")
    feed_all_pets_and_exit()
