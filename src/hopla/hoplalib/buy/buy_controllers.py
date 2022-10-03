#!/usr/bin/env python3
"""
Module with controllers for buying things from the Habitica API.
"""
from dataclasses import dataclass
from typing import NoReturn, Union

import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder


@dataclass
class BuyEnchantedArmoireRequest(HabiticaRequest):
    """HabiticaRequest that buys from the enchanted armoire."""

    @property
    def url(self) -> str:
        """The habitica API buy url."""
        return UrlBuilder(path_extension="/user/buy-armoire").url

    def post_buy_request(self) -> requests.Response:
        """POST a buy request to the habitica API."""
        return requests.post(
            url=self.url,
            headers=self.default_headers,
            timeout=HabiticaRequest.TIMEOUT
        )

    def post_buy_request_get_data_or_exit(self) -> Union[dict, NoReturn]:
        """POST a buy request and return the result, exit if the request failed.

        :return: If successful, the armoire content.
        """
        response: requests.Response = self.post_buy_request()
        # By default, we get way too much JSON info, so filter on "armoire".
        return get_data_or_exit(response)["armoire"]
