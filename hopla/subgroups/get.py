import copy
import logging
from typing import List

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

    response = HabiticaUserRequest().request_user()

    response_json = response.json()
    if response_json["success"]:
        data_items = response_json["data"]["items"]
        if item_group_name == "all":
            click.echo(data_items)
        else:
            click.echo(data_items[item_group_name])
    else:
        click.echo(response_json["message"])


# TODO: aliases
valid_stat_names = click.Choice(["hp", "mp", "exp", "gp", "class", "all"])


@get.command(help="Get a user's stats")
@click.argument("stat_name", type=valid_stat_names, default="all")
def user_stats(stat_name: str):
    """
    Retrieve information from /user .data.user.stats
    """
    log.debug(f"hopla get user-stats stat={stat_name}")

    response = HabiticaUserRequest().request_user()

    user_dict = HabiticaUser(user_dict=response.json()["data"]).user_as_json_str()
    print(user_dict)
    print(user_dict["auth"])

    # response_json = response.json()
    # if response_json["success"]:
    #     data_items = response_json["data"]["stats"]
    #     if stat_name == "all":
    #         click.echo(data_items)
    #         return data_items
    #     else:
    #         click.echo(data_items[stat_name])
    #         return data_items[stat_name]
    # else:
    #     click.echo(response_json["message"])


# username -> 'data.auth.local.username':
# * Your username is used for invitations, @mentions in chat, and messaging.
# * It must be 1 to 20 characters, containing only letters a to z, numbers 0 to 9, hyphens, or underscores, and cannot include any inappropriate terms.
# * is changeable at '<https://habitica.com/user/settings/site>' 'Change Display Name'

# profilename -> 'data.profile.name'
# *  is changeable at '<https://habitica.com/user/settings/site>' under 'Change Display Name'
# profilename is not really in the .data.auth section of /user.. but fits well here

# TODO: aliases
valid_auth_info_names = click.Choice(["username", "email", "profilename", "all"])


@get.command(help="Get user authentication and identification info")
@click.argument("auth_info_name", type=valid_auth_info_names, default="all")
def user_auth(auth_info_name: str):
    log.debug(f"hopla get user-auth auth={auth_info_name}")

    response = HabiticaUserRequest().request_user()
    response_json = response.json()

    if response_json["success"]:
        json_data = response_json["data"]
        json_data_auth = json_data["auth"]
        if auth_info_name == "all":
            click.echo(json_data_auth)
            return json_data_auth
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


@get.command(help="get all user info or query into the user JSON object")
@click.option("--filter", "-f", "filter_string", type=str)
def user_info(filter_string):
    log.debug(f"hopla get user-info filter={filter_string}")

    response = HabiticaUserRequest().request_user()
    response_json = response.json()

    if response_json["success"]:
        user_data = response_json["data"]
        if filter_string:
            filtered_user = HabiticaUser(user_dict=user_data).filter_user(filter_string).user_dict
            click.echo(filtered_user)
            return filtered_user

        else:
            click.echo(user_data)
            return user_data


class HabiticaUserRequest:
    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url
        self.headers = RequestHeaders().get_default_request_headers()

    def request_user(self) -> requests.Response:
        return requests.get(url=self.url, headers=self.headers)


from dataclasses import dataclass
import json


@dataclass(frozen=True)
class HabiticaUser:
    user_dict: dict  # This should be a 200 ok response as json (using Response.json()) when calling the /user endpoint and getting .data

    def user_as_json_str(self, indent=2) -> str:
        return json.dumps(self.user_dict, indent=indent)

    def filter_user(self, filter_string: str):
        """
        Filter this habitica user dict according to the filter_keys.

        [Backus-Naur-Form](https://en.wikipedia.org/wiki/Backus-Naur-Form) for the filter_keys:

            filter_keys ::= [filter_keys]?[,filter_keys]*
            filter_keys   ::= filter_keys[.filter_keys]*

        Examples:
           get all items of a user:                "items"
           get all mounts of a user:               "items.mounts"
           get all mounts and pets of a user:      "items.mounts,items.pets"


        :param filter_string: string to filter the user dict on (e.g. "achievements.streak,purchased.plan")
        :return: a HabiticaUser representing the user with the non-matched keys removed
        """
        result = dict()
        filters: List[str] = filter_string.strip().split(",")

        for filter_keys in filters:
            filter_keys: str = filter_keys.strip()
            print(filter_keys)
            if len(filter_keys) != 0:
                print(result)
                result.update(self._filter_user(user_dict=self.user_dict, filter_keys=filter_keys))

        return HabiticaUser(user_dict=result)

    def _filter_user(self, *, user_dict: dict, filter_keys: str) -> dict:
        """Gets a dict D and a string of form "hi.ya.there"

        >>> self._filter_user(user_dict={"items": {"currentPet": "Wolf-Base", "currentMount": "Aether-Invisible"}},
        ...                   filter_keys="items.currentMount")
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

# @property
# def user_json(self):
#     return json.dumps()
