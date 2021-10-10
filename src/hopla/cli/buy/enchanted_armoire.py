#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla buy enchanted-armoire` command.
"""
import logging
from dataclasses import dataclass
from typing import Final, Optional

import click

from hopla.cli.groupcmds.get_user import HabiticaUser, HabiticaUserRequest
from hopla.hoplalib.buy.buy_controllers import BuyEnchantedArmoireRequest
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.hoplalib.throttling import ApiRequestThrottler

log = logging.getLogger()


def buy_from_enchanted_armoire_once() -> None:
    """buy once from the enchanted armoire"""
    buy_request = BuyEnchantedArmoireRequest()

    buy_data: dict = buy_request.post_buy_request_get_data_or_exit()

    enchanted_armoire_award = JsonFormatter(buy_data).format_with_double_quotes()
    click.echo(enchanted_armoire_award)


def times_until_out_of_gp(gp: float) -> int:
    """Returns how often you can buy from the enchanted_armoire given some budget.

    \f
    :param gp:
    :return:
    """
    enchanted_armoire_price = 100
    times: float = gp / enchanted_armoire_price
    return int(times)  # int will round down positive floats for us


class EnchantedArmoireException(click.UsageError):
    """
    Exception raised when there is an error with
    a `hopla buy enchanted-armoire` invocation.
    """


_TIMES_OPT_NAME: Final[str] = "--times"
_UNTIL_OUT_GP_OPT_NAME: Final[str] = "--until-out-of-gp"


@dataclass(frozen=True)
class BuyEnchantedArmoireCommandHelper:
    """Helper class for the `hopla buy enchanted-armoire` command."""
    requested_times: Optional[int]
    until_out_gp_flag: bool

    def __post_init__(self):
        if self.requested_times is not None and self.until_out_gp_flag is True:
            err_msg = f"{_TIMES_OPT_NAME} and {_UNTIL_OUT_GP_OPT_NAME} are mutually exclusive."
            raise EnchantedArmoireException(message=err_msg)


@click.command()
@click.option(
    _TIMES_OPT_NAME, "-t", "requested_times",
    type=click.IntRange(min=0),
    metavar="[TIMES]",
    help="Number of times to buy from the enchanted-armoire.\n"
         f"Note that {_TIMES_OPT_NAME} cannot be combined with {_UNTIL_OUT_GP_OPT_NAME}"

)
@click.option(
    _UNTIL_OUT_GP_OPT_NAME, "-u", "until_out_of_gp_flag",
    is_flag=True, default=False, show_default=True,
    help="Buy from enchanted-armoire until gp runs out.\n"
         f"Note that {_UNTIL_OUT_GP_OPT_NAME} cannot be combined with {_TIMES_OPT_NAME}"

)
def enchanted_armoire(requested_times: Optional[int],
                      until_out_of_gp_flag: bool):
    """Buy from the enchanted armoire

    -t TIMES - the number of times to buy from the enchanted armoire. Must be at
    least 0. When TIMES and -u are omitted, 1 is the default.

    If no options are specified, you buy once.

    \b
    Examples
    ----
    # Buy once from the enchanted armoire.
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
    BuyEnchantedArmoireCommandHelper(
        requested_times=requested_times, until_out_gp_flag=until_out_of_gp_flag
    )

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
