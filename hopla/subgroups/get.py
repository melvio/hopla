import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


@click.group()
def get():
    pass


valid_item_groups = click.Choice(["pets", "mounts", "food", "gear", "quests", "hatchingPotions", "eggs", "all"])


@get.command()
@click.argument("item_group_name", type=valid_item_groups, default="all")
def user_inventory(item_group_name):
    log.debug("hopla get user-inventory")

    headers = RequestHeaders().get_default_request_headers()
    url = UrlBuilder(path_extension="/user").url

    response = requests.get(url=url, headers=headers)

    json = response.json()
    if json["success"]:
        data_items = json["data"]["items"]
        if item_group_name == "all":
            click.echo(data_items)
        else:
            click.echo(data_items[item_group_name])
    else:
        click.echo(json["message"])
