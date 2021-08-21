import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def buy():
    pass


@buy.command()
# @click.option("--times")
# @click.option("--until-poor")
def enchanted_armoire():
    log.debug("hopla buy enchanted-armoire")

    # TODO: (contact:melvio) after the options are added, we need to loop
    url = UrlBuilder(path_extension="/user/buy-armoire").url
    headers = RequestHeaders().get_default_request_headers()

    response = requests.post(url=url, headers=headers)

    json = response.json()
    click.echo(json["data"]["armoire"])
