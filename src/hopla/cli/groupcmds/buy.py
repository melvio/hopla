"""
The module with CLI code that handles the `hopla buy` group command.
"""
import logging
import time

import click
import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.http import RequestHeaders, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import HabiticaUserRequest, HabiticaUser

log = logging.getLogger()


@click.group()
def buy():
    """
    GROUP to buy things.
    """


def buy_from_enchanted_armoire_once():
    """buy once from the enchanted armoire"""
    url = UrlBuilder(path_extension="/user/buy-armoire").url
    headers = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers)
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

    exceeds_throttle_threshold = exceeds_throttle_limit(times)
    throttle_seconds = 2.5
    if exceeds_throttle_threshold:
        click.echo(f"To prevent overheating Habitica, we'll "
                   f"buy once every {throttle_seconds} seconds")

    for _ in range(times):
        buy_from_enchanted_armoire_once()
        # throttle because we are going to call the API often
        if exceeds_throttle_threshold:
            time.sleep(throttle_seconds)


def exceeds_throttle_limit(times: int) -> bool:
    """Return True if we need Hopla to go easy on the Habitica API."""
    # Remark: When we need to throttle in multiple places, handle this globally, not
    #  here in `buy`.
    requests_throttle_limit = 25
    return times > requests_throttle_limit


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
