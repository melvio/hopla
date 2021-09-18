"""
A module for performing feeding Pet HTTP requests.
"""
import requests
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder


class FeedPostRequester(HabiticaRequest):
    """
    The FeedPostRequester sends a post request to feed a pet.

    Note: this API endpoint expects query params instead
    of a request body (even though it is a HTTP POST).

    [APIDOCS](https://habitica.com/apidoc/#api-User-UserFeed)
    """

    def __init__(self, *,
                 pet_name: str,
                 food_name: str,
                 food_amount: int = 1):
        self.pet_name = pet_name
        self.food_name = food_name
        self.query_params = {"amount": food_amount}


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
        return requests.post(url=self.feed_pet_food_url, headers=self.default_headers,
                             params=self.query_params)
