import logging
import click
import requests
import time

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def buy():
    pass


def buy_from_enchanted_armoire_once():
    # TODO: (contact:melvio) after the options are added, we need to loop
    url = UrlBuilder(path_extension="/user/buy-armoire").url
    headers = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers)

    json = response.json()
    click.echo(json["data"]["armoire"])


@buy.command()
@click.option("--times", "-t",
              default=1,
              type=click.IntRange(min=0),
              help="number of times to buy from the enchanted-armoire")
@click.option("--until-poor", "-u", is_flag=True, help="buy from enchanted-armoire until gp runs out")
def enchanted_armoire(times: int, until_poor: bool):
    log.debug(f"hopla buy enchanted-armoire times={times}, until_poor={until_poor}")

    # TODO (contact:melvio) when until_poor=True, calculate the user's gp
    # * this can be done by hopla itself once user-inventory gp has been implemented

    for _ in range(times):
        buy_from_enchanted_armoire_once()
        if times > 28:
            time.sleep(secs=2)  # throttle when we are going to call the API often
