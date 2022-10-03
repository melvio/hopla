"""
A module for performing feeding Pet HTTP requests.
"""
from typing import NoReturn, Optional, Union

import requests

from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.zoo.feed_clickhelper import get_feed_data_or_exit
from hopla.hoplalib.zoo.zoofeed_algorithms import FeedPlanItem


class FeedPostRequester(HabiticaRequest):
    """
    The FeedPostRequester sends a post request to feed a pet.

    Note: this API endpoint expects query params instead
    of a request body (even though it is a HTTP POST).

    [APIDOCS](https://habitica.com/apidoc/#api-User-UserFeed)
    """
    _DEFAULT_FOOD_AMOUNT = 1

    def __init__(self, *,
                 pet_name: str,
                 food_name: str,
                 food_amount: Optional[int] = _DEFAULT_FOOD_AMOUNT):
        self.pet_name = pet_name
        self.food_name = food_name
        self.query_params = {
            "amount": food_amount or FeedPostRequester._DEFAULT_FOOD_AMOUNT
        }

    @property
    def path(self) -> str:
        """Return the URL used to feed a pet"""
        return f"/user/feed/{self.pet_name}/{self.food_name}"

    @property
    def feed_pet_food_url(self) -> str:
        """Return the url to feed a pet"""
        return UrlBuilder(path_extension=self.path).url

    def post_feed_request(self) -> requests.Response:
        """Performs the feed pet post requests and return the response"""
        return requests.post(
            url=self.feed_pet_food_url,
            headers=self.default_headers,
            params=self.query_params,
            timeout=HabiticaRequest.TIMEOUT
        )

    def post_feed_request_get_data_or_exit(self) -> Union[NoReturn, dict]:
        """
        Performs the feed pet post requests and return
        the feed response if successful. Else exit

        :return:
        """
        response: requests.Response = self.post_feed_request()
        return get_feed_data_or_exit(response)

    @classmethod
    def build_from(cls, feed_item: FeedPlanItem) -> "FeedPostRequester":
        """Create a request from a feed plan item."""
        return FeedPostRequester(
            pet_name=feed_item.pet_name,
            food_name=feed_item.food_name,
            food_amount=feed_item.times
        )
