import copy
import logging
import json
import click
import requests

from typing import List
from dataclasses import dataclass

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


@click.group()
def get():
    """GROUP for getting information from habitica"""
    pass


def handle_response(api_response: requests.Response):
    """Returns the data of a response if successful, else print error message

    :param api_response:
    :return:
    """
    response_json = api_response.json()
    if response_json["success"]:
        return response_json["data"]
    else:
        log.debug(f"received: {response_json}")
        click.echo([response_json["message"]])


valid_item_groups = click.Choice(["pets", "mounts", "food", "gear", "quests", "hatchingPotions", "eggs", "all"])


@get.command()
@click.argument("item_group_name", type=valid_item_groups, default="all")
def user_inventory(item_group_name) -> dict:
    """Get items from the user's inventory

    If no specific item group is specified,

    \f
    :param item_group_name: The type of items in the inventory (default: all)
    :return: The specified inventory
    """
    log.debug(f"hopla get user-inventory item_group={item_group_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = handle_response(response)

    data_items = response_data["items"]
    if item_group_name == "all":
        click.echo(data_items)
        return data_items
    else:
        click.echo(data_items[item_group_name])
        return data_items


valid_stat_names = click.Choice(["hp", "mp", "exp", "gp", "lvl", "class", "all"])


def from_alias_to_canonical_name(stat_name: str):
    if stat_name in ["mana", "mana-points", "manapoints"]:
        return "mp"
    elif stat_name in ["health"]:
        return "hp"
    elif stat_name in ["xp", "experience"]:
        return "exp"
    elif stat_name in ["gold"]:
        return "gp"
    elif stat_name in ["level"]:
        return "lvl"
    else:
        return stat_name


@get.command(context_settings=dict(token_normalize_func=from_alias_to_canonical_name))
@click.argument("stat_name", type=valid_stat_names, default="all")
def user_stats(stat_name: str):
    """Get the stats of a user"""
    log.debug(f"hopla get user-stats stat={stat_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = handle_response(response)

    data_stats = response_data["stats"]
    if stat_name == "all":
        click.echo(data_stats)
        return data_stats
    else:
        click.echo(data_stats[stat_name])
        return data_stats[stat_name]


# TODO: aliases
valid_auth_info_names = click.Choice(["username", "email", "profilename", "all"])


# username -> 'data.auth.local.username':
# * Your username is used for invitations, @mentions in chat, and messaging.
# * It must be 1 to 20 characters, containing only letters a to z, numbers 0 to 9, hyphens, or underscores, and cannot include any inappropriate terms.
# * is changeable at '<https://habitica.com/user/settings/site>' 'Change Display Name'

# profilename -> 'data.profile.name'
# *  is changeable at '<https://habitica.com/user/settings/site>' under 'Change Display Name'
# profilename is not really in the .data.auth section of /user.. but fits well here


@get.command()
@click.argument("auth_info_name", type=valid_auth_info_names, default="all")
def user_auth(auth_info_name: str):
    """Get user authentication and identification info"""
    log.debug(f"hopla get user-auth auth={auth_info_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = handle_response(response)

    json_data_auth = response_data["auth"]
    if auth_info_name == "all":
        click.echo(json_data_auth)
        return json_data_auth
    if auth_info_name == "profilename":
        profile_name = response_data["profile"]["name"]
        click.echo(profile_name)
        return profile_name
    else:
        # TODO no support for non-local data yet (e.g. google SSO)
        auth_info = json_data_auth["local"][auth_info_name]
        click.echo(auth_info)
        return auth_info


@get.command()
@click.option("--filter", "-f", "filter_string", type=str)
def user_info(filter_string: str):
    """Return user information

    If no filter_string is given, get all user info.
    Else returns the result of filtering the user's info on the specified filter_string

    -f filters the user according to the filter_string.

    [BNF](https://en.wikipedia.org/wiki/Backus-Naur-Form)
    for the filter_string:

    \b
        filter_keys ::= [filter_keys]?[,filter_keys]*
        filter_keys ::= filter_keys[.filter_keys]*

    \b
    Examples:
    ---
    # get all items of a user:
    hopla get user-info ---filter "items"

    \b
    # get all mounts
    hopla get user-info ---filter "items.mounts"

    \b
    # get all mounts+pets
    hopla get user-info ---filter "items.mounts,items.pets"

    \b
    # get streaks+completed quests
    hopla get user-info -f "achievements.streak,achievements.quests"

    \b
    # get contributor status, croncount, profile description, and user id
    hopla get user-info -f "contributor,flags.cronCount,profile.blurb,id"


    \f
    :param filter_string: string to filter the user dict on (e.g. "achievements.streak,purchased.plan")
    :return
    """

    log.debug(f"hopla get user-info filter={filter_string}")

    response = HabiticaUserRequest().request_user()
    response_json = response.json()

    if response_json["success"]:
        user_data = response_json["data"]
        if filter_string:
            filtered_user = HabiticaUser(user_dict=user_data).filter_user(filter_string).user_as_json_str()
            click.echo(filtered_user)
            return filtered_user

        else:
            click.echo(json.dumps(user_data, indent=2))
            return user_data


class HabiticaUserRequest:
    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url
        self.headers = RequestHeaders().get_default_request_headers()

    def request_user(self) -> requests.Response:
        return requests.get(url=self.url, headers=self.headers)


@dataclass(frozen=True)
class HabiticaUser:
    user_dict: dict  # This should be a 200 ok response as json (using Response.json()) when calling the /user endpoint and getting .data

    def user_as_json_str(self, indent=2) -> str:
        return json.dumps(self.user_dict, indent=indent)

    def filter_user(self, filter_string: str):
        result = dict()
        filters: List[str] = filter_string.strip().split(",")

        for filter_keys in filters:
            filter_keys: str = filter_keys.strip()
            if len(filter_keys) != 0:
                result.update(self._filter_user(user_dict=self.user_dict, filter_keys=filter_keys))

        return HabiticaUser(user_dict=result)

    def _filter_user(self, *, user_dict: dict, filter_keys: str) -> dict:
        """ Gets a starting dict D and uses filter_keys of form "hi.ya.there" to get
            {filter_keys: D["hi"]["ya"]["there"]} or {filter_string: {}} if D["hi"]["ya"]["there"]
            does not exist.

        TODO: include doctests in the build process [docs](https://docs.python.org/3/library/doctest.html)
        >>> self._filter_user(user_dict={"items": {"currentPet": "Wolf-Base", "currentMount": "Aether-Invisible"}},
        ...                   filter_keys = "items.currentMount")
        {"items.currentMount": "Aether-Invisible"}

        :param user_dict:
        :param filter_keys:
        :return: we return {filter_string: D["hi"]["ya"]["there"]} or {filter_string: {}} if there is no such item
        """
        start_dict = copy.deepcopy(user_dict)
        dict_keys: List[str] = filter_keys.split(".")
        for dict_key in dict_keys:
            if start_dict is not None:
                start_dict = start_dict.get(dict_key)
            else:
                log.debug(f"Didn't match anything with the given filter={filter_keys}")
                return {filter_keys: {}}
        return {filter_keys: start_dict}
