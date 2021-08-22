import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


@click.group()
def get():
    pass


# TODO: aliases
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


# TODO: aliases
valid_stat_names = click.Choice(["hp", "mp", "exp", "gp", "class", "all"])


@get.command(help="Get a user's stats")
@click.argument("stat_name", type=valid_stat_names, default="all")
def user_stats(stat_name: str):
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
            return data_items[stat_name]
    else:
        click.echo(json["message"])


# username -> 'data.auth.local.username':
# * Your username is used for invitations, @mentions in chat, and messaging.
# * It must be 1 to 20 characters, containing only letters a to z, numbers 0 to 9, hyphens, or underscores, and cannot include any inappropriate terms.
# * is changeable at '<https://habitica.com/user/settings/site>' 'Change Display Name'

# profilename -> 'profile.name'
# *  is changeable at '<https://habitica.com/user/settings/site>' under 'Change Display Name'
# profilename is not really in the .data.auth section of /user.. but fits well here

# TODO: aliases
valid_auth_info_names = click.Choice(["username", "email", "profilename", "all"])


@get.command(help="Get user authentication and identification info")
@click.argument("auth_info_name", type=valid_auth_info_names, default="all")
def user_auth(auth_info_name: str):
    log.debug(f"hopla get user-auth auth={auth_info_name}")

    response = HabiticaUserRequest().get_user()
    json = response.json()

    if json["success"]:
        json_data = json["data"]
        json_data_auth = json_data["auth"]
        if auth_info_name == "all":
            click.echo(json_data_auth)
            return  json_data_auth
        if auth_info_name == "profilename":
            profile_name = json_data["profile"]["name"]
            click.echo(profile_name)
            return profile_name
        else:
            # TODO no support for non-local data yet (e.g. google SSO)
            # use 'all' instead and filter
            auth_info = json_data_auth["local"][auth_info_name]
            click.echo(auth_info)
            return auth_info





class HabiticaUserRequest:
    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url
        self.headers = RequestHeaders().get_default_request_headers()

    def get_user(self) -> requests.Response:
        return requests.get(url=self.url, headers=self.headers)
