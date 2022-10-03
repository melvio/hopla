#!/usr/bin/env python3
"""
Module that talks to the Habitica API to manage a Habitica user object.
"""
import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.user.usermodels import HabiticaUser


class HabiticaUserRequest(HabiticaRequest):
    """Class that requests a user model from the Habitica API"""

    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url

    def request_user(self) -> requests.Response:
        """Perform the user get request and return the response"""
        return requests.get(
            url=self.url,
            headers=self.default_headers,
            timeout=HabiticaRequest.TIMEOUT
        )

    def request_user_data_or_exit(self) -> HabiticaUser:
        """
        Function that request the user from habitica and returns
        a HabiticaUser if the request was successful. Else exits.
        """
        user_response: requests.Response = self.request_user()
        user_data: dict = get_data_or_exit(user_response)
        return HabiticaUser(user_dict=user_data)
