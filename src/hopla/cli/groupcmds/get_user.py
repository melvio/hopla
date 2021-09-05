"""
The module with CLI code that handles the `hopla get` group command.
"""
import copy
import logging
from dataclasses import dataclass
from typing import List

import click
import requests

from hopla.hoplalib.clickhelper import data_on_success_else_exit
from hopla.hoplalib.http import RequestHeaders, UrlBuilder

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

    def get_auth(self) -> dict:
        """Index the user_dict for 'authenticate' and return the result"""
        return self["auth"]

    def get_gems(self):
        """Get the number of gems of a user.

        gems are stored in the 'balance' field. 1 'balance' equals 4 gems
        [see](https://habitica.fandom.com/wiki/Gems#Information_for_Developers)
        """
        balance = self.user_dict["balance"]
        return balance * 4

    def filter_user(self, filter_string: str) -> dict:
        """Return a dict after filtering."""
        # TODO: this code is generic, it can be used to filter any dict
        #       move it out of this class and reuse
        result = {}
        filters: List[str] = filter_string.strip().split(",")

        for filter_keys in filters:
            filter_keys: str = filter_keys.strip()
            if len(filter_keys) != 0:
                result.update(self._filter_user(user_dict=self.user_dict,
                                                filter_keys=filter_keys))

        return result

    def _filter_user(self, *, user_dict: dict, filter_keys: str) -> dict:
        """ Gets a starting dict D and uses filter_keys of form "hi.ya.there" to get
            {filter_keys: D["hi"]["ya"]["there"]} or {filter_string: {}} if D["hi"]["ya"]["there"]
            does not exist.

        >>> HabiticaUser({})._filter_user(
        ...     user_dict={"items": {"currentPet":"Wolf-Base", "currentMount":"Aether-Invisible"}},
        ...     filter_keys = "items.currentMount")
        {'items.currentMount': 'Aether-Invisible'}

        :param user_dict:
        :param filter_keys:
        :return: we return {filter_string: D["hi"]["ya"]["there"]} or
                 {filter_string: {}} if there is no such item
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


class HabiticaUserRequest:
    """Class that requests a user model from the Habitica API"""

    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url
        self.headers = RequestHeaders().get_default_request_headers()

    def request_user(self) -> requests.Response:
        """Perform the user get request and return the response"""
        return requests.get(url=self.url, headers=self.headers)

    def request_user_data_on_fail_exit(self) -> HabiticaUser:
        """
        Function that request the user from habitica and returns
        a HabiticaUser if the request was successful. Else exits.
        """
        user_response: requests.Response = self.request_user()
        user_data: dict = data_on_success_else_exit(user_response)
        return HabiticaUser(user_dict=user_data)


pass_user = click.make_pass_decorator(HabiticaUser)


@click.group()
@click.pass_context
def get_user(ctx: click.Context) -> HabiticaUser:
    """
    GROUP for getting user information from Habitica.
    """
    log.debug("hopla get-user")
    user: HabiticaUser = HabiticaUserRequest().request_user_data_on_fail_exit()
    ctx.obj = user
    return user

# TODO: add jq back again https://pypi.org/project/jq/
#       or https://pypi.org/project/pyjq/
