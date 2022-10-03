#!/usr/bin/env python3
"""
Module with spell casting logic.
"""
from dataclasses import dataclass

import requests

from hopla.hoplalib.cast.spellmodel import Spell
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder


@dataclass
class PostCastRequest(HabiticaRequest):
    """HabiticaRequester that POSTs to the spell cast endpoint.

    [APIDOCS](https://habitica.com/apidoc/#api-User-UserCast)
    """
    spell: Spell

    @property
    def url(self) -> str:
        """Get the url"""
        path_extension = f"/user/class/cast/{self.spell.name}"
        return UrlBuilder(path_extension=path_extension).url

    def post_spell(self) -> requests.Response:
        """Perform the user get request and return the response"""
        return requests.post(
            url=self.url,
            headers=self.default_headers,
            timeout=HabiticaRequest.TIMEOUT
        )
