import logging
import click
import requests
import time

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders
from hopla.subgroups import get

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def buy():
    """group command to buy things"""
    pass


def buy_from_enchanted_armoire_once():
    # TODO: (contact:melvio) after the options are added, we need to loop
    url = UrlBuilder(path_extension="/user/buy-armoire").url
    headers = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers)

    json = response.json()
    click.echo(json["data"]["armoire"])


def times_until_poor(gp: float) -> int:
    enchanted_armoire_price = 100
    times: float = gp / enchanted_armoire_price
    return int(times)  # int will round down positive floats for us


@buy.command()
@click.option("--times", "-t",
              default=1,
              type=click.IntRange(min=0),
              help="number of times to buy from the enchanted-armoire")
@click.option("--until-poor", "-u", is_flag=True, help="buy from enchanted-armoire until gp runs out")
@click.pass_context
def enchanted_armoire(ctx, times: int, until_poor: bool):
    """ Buy from the enchanted armoire

    By default you only buy once. Use the options to buy more often.
    """
    log.debug(f"hopla buy enchanted-armoire times={times}, until_poor={until_poor}")

    # TODO (contact:melvio) when until_poor=True, calculate the user's gp
    # * this can be done by hopla itself once user-inventory gp has been implemented
    # https://click.palletsprojects.com/en/8.0.x/options/#boolean-flags

    # TODO: (contact:melvio) --until-poor and --times N should be mutually exclusive options:
    #  and I dont think this is the case right now.
    #  * if it is the case: this TODO is DONE
    #  * else: ensure the options become mutually exclusive (right now, the impl overwrites -t if -u is also given)

    if until_poor:
        # get gp and calculate how many times we should buy
        gp = ctx.invoke(get.user_stats, stat_name="gp")  # TODO: this will echo 'gp': fix this
        times = times_until_poor(gp)

    # TODO: maybe also use gp to limit the --times option
    for _ in range(times):
        buy_from_enchanted_armoire_once()
        if times > 28:
            # throttle because we are going to call the API often
            seconds = 2
            time.sleep(seconds)
