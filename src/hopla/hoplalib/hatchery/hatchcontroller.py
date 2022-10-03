#!/usr/bin/env python3
"""
Module that talks to the Habitica API to hatch eggs.
"""
from dataclasses import dataclass

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
        return requests.post(
            url=self.url,
            headers=self.default_headers,
            timeout=HabiticaRequest.TIMEOUT
        )
