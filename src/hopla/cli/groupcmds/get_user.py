"""
The module with CLI code that handles the `hopla get` group command.
"""
import logging
from dataclasses import dataclass
from typing import Dict

import click
import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder

log = logging.getLogger()


@dataclass(frozen=True)
class HabiticaUser:
    """
    Class representing a user model.

    The user_dict is assumed to be returned from a 200 ok Response as (using
    Response.json()) when calling the /user endpoint and getting .data
    """
    user_dict: dict

    def __getitem__(self, key):
        return self.user_dict.__getitem__(key)

    def get_stats(self) -> dict:
        """Index the user_dict for 'stats' and return the result"""
        return self["stats"]

    def get_inventory(self) -> dict:
        """Index the user_dict for 'items' and return the result"""
        return self["items"]

    def get_pets(self) -> dict:
        """Return the pets of a user."""
        return self.get_inventory()["pets"]

    def get_mounts(self) -> dict:
        """Return the mounts of a user."""
        return self.get_inventory()["mounts"]

    def get_food(self) -> Dict[str, int]:
        """Return the food that the user has"""
        return self.get_inventory()["food"]

    def get_auth(self) -> dict:
        """Index the user_dict for 'auth' and return the result"""
        return self["auth"]

    def get_gems(self) -> int:
        """Get the number of gems of a user.

        gems are stored in the 'balance' field. 1 'balance' equals 4 gems
        [see](https://habitica.fandom.com/wiki/Gems#Information_for_Developers)
        """
        balance = self["balance"]
        return int(balance * 4)


class HabiticaUserRequest(HabiticaRequest):
    """Class that requests a user model from the Habitica API"""

    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url

    def request_user(self) -> requests.Response:
        """Perform the user get request and return the response"""
        return requests.get(url=self.url, headers=self.default_headers)

    def request_user_data_or_exit(self) -> HabiticaUser:
        """
        Function that request the user from habitica and returns
        a HabiticaUser if the request was successful. Else exits.
        """
        user_response: requests.Response = self.request_user()
        user_data: dict = get_data_or_exit(user_response)
        return HabiticaUser(user_dict=user_data)


pass_user = click.make_pass_decorator(HabiticaUser)


@click.group()
@click.pass_context
def get_user(ctx: click.Context) -> HabiticaUser:
    """
    GROUP for getting user information from Habitica.
    """
    log.debug("hopla get-user")
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    ctx.obj = user
    return user
