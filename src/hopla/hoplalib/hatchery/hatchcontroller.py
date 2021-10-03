#!/usr/bin/env python3
"""
Module that talks to the Habitica API to hatch eggs.
"""
from dataclasses import dataclass
from typing import Any, Dict

import requests
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder


@dataclass
class HatchRequester(HabiticaRequest):
    """HatchRequester that POSTs to hatch endpoint.

    [APIDOCS](https://habitica.com/apidoc/#api-User-UserHatch)
    """
    egg_name: str
    hatch_potion_name: str

    @property
    def url(self) -> str:
        """Hatch endpoint with egg and hatch_potion_name as path params."""
        path_extension = f"/user/hatch/{self.egg_name}/{self.hatch_potion_name}"
        return UrlBuilder(path_extension=path_extension).url

    def post_hatch_egg_request(self) -> requests.Response:
        """Perform a POST request on the Habitica API to hatch an egg."""
        return requests.post(url=self.url, headers=self.default_headers)

    def post_hatch_egg(self) -> str:
        """Perform a POST request on the Habitica API to hatch an egg, and
        return a str that can be nicely printed to the terminal.
        """
        response: requests.Response = self.post_hatch_egg_request()
        response_json: Dict[str, Any] = response.json()
        if response_json["success"] is True:
            return f"Successfully hatched a {self.egg_name}-{self.hatch_potion_name}."
        return f"{response_json['error']}: {response_json['message']}"
