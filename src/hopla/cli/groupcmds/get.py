"""
The module with CLI code that handles the `hopla get` group command.
"""
import copy
import logging
from dataclasses import dataclass
from typing import List

import click
import requests

from hopla.hoplalib.http import RequestHeaders, UrlBuilder

log = logging.getLogger()


@click.group()
def get():
    """GROUP for getting information from habitica"""


# TODO: add jq back again https://pypi.org/project/jq/
#       or https://pypi.org/project/pyjq/


class HabiticaUserRequest:
    """Class that requests a user model from the Habitica API"""

    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url
        self.headers = RequestHeaders().get_default_request_headers()

    def request_user(self) -> requests.Response:
        return requests.get(url=self.url, headers=self.headers)


@dataclass(frozen=True)
class HabiticaUser:
    """
    Class representing a user model.

    The user_dict is assumed to be returned from a 200 ok Response as (using
    Response.json()) when calling the /user endpoint and getting .data
    """
    user_dict: dict

    def get_stats(self) -> dict:
        """Index the user_dict for 'stats' and return the result"""
        return self.user_dict["stats"]

    def get_inventory(self) -> dict:
        """Index the user_dict for 'items' and return the result"""
        return self.user_dict["items"]

    def get_auth(self) -> dict:
        """Index the user_dict for 'auth' and return the result"""
        return self.user_dict["auth"]

    def get_gems(self):
        """Get the number of gems of a user.

        gems are stored in the 'balance' field. 1 'balance' equals 4 gems
        [see](https://habitica.fandom.com/wiki/Gems#Information_for_Developers)
        """
        balance = self.user_dict["balance"]
        return balance * 4

    def filter_user(self, filter_string: str) -> dict:
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


if __name__ == "__main__":
    import doctest

    doctest.testmod()
