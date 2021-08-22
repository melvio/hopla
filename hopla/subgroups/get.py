import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


@click.group()
def get():
    pass


valid_item_groups = click.Choice(["pets", "mounts", "food", "gear", "quests", "hatchingPotions", "eggs", "all"])


@get.command(help="Get items from the user's inventory")
@click.argument("item_group_name", type=valid_item_groups, default="all")
def user_inventory(item_group_name):
    log.debug(f"hopla get user-inventory item_group={item_group_name}")

    response = HabiticaUserRequest().get_user()

    json = response.json()
    if json["success"]:
        data_items = json["data"]["items"]
        if item_group_name == "all":
            click.echo(data_items)
        else:
            click.echo(data_items[item_group_name])
    else:
        click.echo(json["message"])


valid_stat_names = click.Choice(["hp", "mp", "exp", "gp", "class", "all"])


@get.command(help="Get a user's stats")
@click.argument("stat_name", type=valid_stat_names, default="all")
def user_stats(stat_name):
    """
    Retrieve information from /user .data.user.stats
    """
    log.debug(f"hopla get user-stats stat={stat_name}")

    response = HabiticaUserRequest().get_user()

    json = response.json()
    if json["success"]:
        data_items = json["data"]["stats"]
        if stat_name == "all":
            click.echo(data_items)
        else:
            click.echo(data_items[stat_name])
    else:
        click.echo(json["message"])


class HabiticaUserRequest:
    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url
        self.headers = RequestHeaders().get_default_request_headers()

    def get_user(self) -> requests.Response:
        return requests.get(url=self.url, headers=self.headers)
