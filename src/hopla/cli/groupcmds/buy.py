"""
The module with CLI code that handles the `hopla buy` group command.
"""
from dataclasses import dataclass
import logging

import click
import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import HabiticaUserRequest, HabiticaUser
from hopla.hoplalib.throttling import ApiRequestThrottler

log = logging.getLogger()


@click.group()
def buy():
    """
    GROUP to buy things.
    """


@dataclass
class BuyEnchantedArmoireRequest(HabiticaRequest):
    """HabiticaRequest that buys from the enchanted armoire."""

    @property
    def url(self):
        """The habitica API buy url."""
        return UrlBuilder(path_extension="/user/buy-armoire").url

    def post_buy_request(self) -> requests.Response:
        """Post a buy request to the habitica API."""
        return requests.post(url=self.url, headers=self.default_headers)


def buy_from_enchanted_armoire_once():
    """buy once from the enchanted armoire"""
    buy_request = BuyEnchantedArmoireRequest()

    response: requests.Response = buy_request.post_buy_request()
    buy_data = get_data_or_exit(response)

    # By default, we get way too much JSON info, so filter on "armoire".
    enchanted_armoire_award = JsonFormatter(buy_data["armoire"]).format_with_double_quotes()
    click.echo(enchanted_armoire_award)


def times_until_poor(gp_budget: float) -> int:
    """Returns how many times you can buy from enchanted_armoire given some budget.

    \f
    :param gp_budget:
    :return:
    """
    enchanted_armoire_price = 100
    times: float = gp_budget / enchanted_armoire_price
    return int(times)  # int will round down positive floats for us


@buy.command()
@click.option("--times", "-t", "requested_times",
              type=click.IntRange(min=0),
              metavar="[TIMES]",
              help="number of times to buy from the enchanted-armoire")
@click.option("--until-poor/--no-until-poor", "-u", "until_poor_flag",
              help="buy from enchanted-armoire until gp runs out",
              default=False, show_default=True)
def enchanted_armoire(requested_times: int, until_poor_flag: bool):
    """Buy from the enchanted armoire

    TIMES - the number of times to buy from the enchanted armoire. Must be at least 0.
    When TIMES is omitted, 1 is the default. When TIMES is larger than the budget allows,
    --until-poor will be used instead. This behavior is likely to change in the
    future: <https://github.com/melvio/hopla/issues/100>

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
    $ hopla buy enchanted-armoire --until-poor
    $ hopla buy enchanted-armoire -u
    """
    log.debug(f"hopla buy enchanted-armoire times={requested_times}, until_poor={until_poor_flag}")

    times: int = get_buy_times_within_budget(until_poor_flag=until_poor_flag,
                                             requested_times=requested_times)

    buy_requests = [buy_from_enchanted_armoire_once for _ in range(times)]
    dispatcher = ApiRequestThrottler(buy_requests)
    for buy_request in dispatcher.release():
        _ = buy_request()


def get_buy_times_within_budget(until_poor_flag: bool,
                                requested_times: int) -> int:
    """Return how often we can buy, given the requested amount and our budget."""
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    budget: float = user["stats"]["gp"]

    max_times = times_until_poor(budget)
    if until_poor_flag:
        requested_times = max_times
    elif requested_times is None:
        requested_times = 1

    times = min(max_times, requested_times)
    click.echo(f"The current budget is {int(budget)}gp.\n"
               f"Buying: {times} times.")
    return times
