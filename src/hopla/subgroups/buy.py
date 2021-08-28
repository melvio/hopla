import logging
import click
import requests
import time

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders
from hopla.hoplalib.ClickUtils import data_on_success_else_exit
from hopla.hoplalib.OutputFormatter import JsonFormatter

from hopla.subgroups import get

log = logging.getLogger()


@click.group()
def buy():
    """GROUP to buy things"""
    pass


def buy_from_enchanted_armoire_once():
    url = UrlBuilder(path_extension="/user/buy-armoire").url
    headers = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers)
    buy_data = data_on_success_else_exit(response)

    # by default we get way too much info in the json so filter on "armoire"
    enchanted_armoire_award = JsonFormatter(buy_data["armoire"]).format_with_double_quotes()
    click.echo(enchanted_armoire_award)


def times_until_poor(gp: float) -> int:
    enchanted_armoire_price = 100
    times: float = gp / enchanted_armoire_price
    return int(times)  # int will round down positive floats for us


@buy.command()
@click.option("--times", "-t",
              default=1,
              type=click.IntRange(min=0),
              metavar="[TIMES]",
              help="number of times to buy from the enchanted-armoire")
@click.option("--until-poor", "-u", is_flag=True, help="buy from enchanted-armoire until gp runs out")
@click.pass_context
def enchanted_armoire(ctx, times: int, until_poor: bool):
    """Buy from the enchanted armoire

    TIMES - the number of times to buy from the enchanted armoire. Must be at least 0.
    When TIMES is omitted, 1 is the default. When TIMES is larger than the budget allows,
    --until-poor will be used instead.

    If no options are specified, you buy once.

    """
    log.debug(f"hopla buy enchanted-armoire times={times}, until_poor={until_poor}")

    # TODO: (contact:melvio) --until-poor and --times N should be mutually exclusive options:
    #  and I dont think this is the case right now.
    #  * if it is the case: this TODO is DONE
    #  * else: ensure the options become mutually exclusive (right now, the impl overwrites -t if -u is also given)

    # get gp and calculate how many times we should buy
    click.echo("starting gp: ", nl=False)
    budget = ctx.invoke(get.user_stats, stat_name="gp")
    max_times = times_until_poor(budget)

    if max_times < times:
        click.echo(f"You can only buy {max_times} times instead of requested {times} times")
        times = max(max_times, times)
    if times != 1:
        click.echo(f"I will buy {times} times for you.")

    # TODO: maybe also use gp to limit the --times option
    for _ in range(times):
        buy_from_enchanted_armoire_once()
        if times > 28:
            # throttle because we are going to call the API often
            seconds = 2
            time.sleep(seconds)
