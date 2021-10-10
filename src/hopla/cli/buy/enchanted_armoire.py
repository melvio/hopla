#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla buy enchanted-armoire` command.
"""
from dataclasses import dataclass
import logging
from typing import NoReturn, Optional, Union

import click
import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import HabiticaUserRequest, HabiticaUser
from hopla.hoplalib.throttling import ApiRequestThrottler

log = logging.getLogger()


@dataclass
class BuyEnchantedArmoireRequest(HabiticaRequest):
    """HabiticaRequest that buys from the enchanted armoire."""

    @property
    def url(self) -> str:
        """The habitica API buy url."""
        return UrlBuilder(path_extension="/user/buy-armoire").url

    def post_buy_request(self) -> requests.Response:
        """POST a buy request to the habitica API."""
        return requests.post(url=self.url, headers=self.default_headers)

    def post_buy_request_get_data_or_exit(self) -> Union[dict, NoReturn]:
        """POST a buy request and return the result, exit if the request failed.

        :return: If successful, the armoire content.
        """
        response: requests.Response = self.post_buy_request()
        # By default, we get way too much JSON info, so filter on "armoire".
        return get_data_or_exit(response)["armoire"]


def buy_from_enchanted_armoire_once():
    """buy once from the enchanted armoire"""
    buy_request = BuyEnchantedArmoireRequest()

    buy_data: dict = buy_request.post_buy_request_get_data_or_exit()

    enchanted_armoire_award = JsonFormatter(buy_data).format_with_double_quotes()
    click.echo(enchanted_armoire_award)


def times_until_out_of_gp(gp: float) -> int:
    """Returns how many times you can buy from enchanted_armoire given some budget.

    \f
    :param gp:
    :return:
    """
    enchanted_armoire_price = 100
    times: float = gp / enchanted_armoire_price
    return int(times)  # int will round down positive floats for us


@click.command()
@click.option(
    "--times", "-t", "requested_times",
    type=click.IntRange(min=0),
    metavar="[TIMES]",
    help="number of times to buy from the enchanted-armoire")
@click.option(
    "--until-out-of-gp", "-u", "until_out_of_gp_flag",
    is_flag=True, default=False, show_default=True,
    help="buy from enchanted-armoire until gp runs out"
)
def enchanted_armoire(requested_times: int,
                      until_out_of_gp_flag: bool):
    """Buy from the enchanted armoire

    TIMES - the number of times to buy from the enchanted armoire. Must be at least 0.
    When TIMES is omitted, 1 is the default.

    If no options are specified, you buy once.

    \b
    Examples
    ----
    # buy once
    $ hopla buy enchanted-armoire

    \b
    # buy 3 times
    $ hopla buy enchanted-armoire -t3
    $ hopla buy enchanted-armoire -t 3
    $ hopla buy enchanted-armoire --times 3
    $ hopla buy enchanted-armoire --times=3

    \b
    # buy until you cannot afford the enchanted-armoire anymore
    $ hopla buy enchanted-armoire --until-out-of-gp
    $ hopla buy enchanted-armoire -u
    """
    log.debug(f"hopla buy enchanted-armoire {requested_times=}, {until_out_of_gp_flag=}")

    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    times: int = get_buy_times_within_budget(user=user,
                                             until_out_of_gp_flag=until_out_of_gp_flag,
                                             requested_times=requested_times)

    buy_requests = [buy_from_enchanted_armoire_once for _ in range(times)]
    dispatcher = ApiRequestThrottler(buy_requests)
    dispatcher.execute_all_requests()


def get_buy_times_within_budget(*, user: HabiticaUser,
                                until_out_of_gp_flag: bool,
                                requested_times: Optional[int]) -> int:
    """Return how often we can buy, given the requested amount and our budget."""
    budget: float = user.get_gp()

    max_times = times_until_out_of_gp(budget)
    if until_out_of_gp_flag:
        wanted_times = max_times
    else:
        wanted_times = requested_times or 1

    times = min(max_times, wanted_times)
    click.echo(f"The current budget is {int(budget)}gp.\n"
               f"Buying: {times} times.", err=True)
    return times
