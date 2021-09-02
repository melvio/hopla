"""
The module with CLI code that handles the `hopla feed` command.
"""
import logging

import click
import requests

from hopla.hoplalib.clickhelper import data_on_success_else_exit
from hopla.hoplalib.http import RequestHeaders, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.hoplalib.clickhelper import FeedingData

log = logging.getLogger()


class PetFeedPostRequester:
    """
    The PetFeedPostRequester sends a post request to feed a pet.

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
    def request_headers(self) -> dict:
        """Return the required headers for a feed-pet post request."""
        return RequestHeaders().get_default_request_headers()

    @property
    def path(self) -> str:
        """Return the URL used to feed a pet"""
        return f"/user/feed/{self.pet_name}/{self.food_name}"

    @property
    def feed_pet_food_url(self) -> str:
        """Return the url to feed a pet"""
        return UrlBuilder(path_extension=self.path).url

    def post_feed_pet_food_request(self) -> requests.Response:
        """Performs the feed pet post requests and return the response"""
        return requests.post(
            url=self.feed_pet_food_url,
            headers=self.request_headers,
            params=self.query_params
        )


# pets can eat up to 50 units of non-preferred foods
# TODO: Not sure if we want to clamp=True (which results
#  in 100 automatically becomes max, -10 becomes min, instead of failing
#   with an click validation error message)
# * Look into other options first, such as; --until-mount
valid_feeding_amount = click.IntRange(min=0, max=50, clamp=False)


@click.command()
@click.argument("pet_name", type=FeedingData.VALID_PET_NAMES, metavar="PET_NAME")
@click.argument("food_name", type=FeedingData.VALID_FOOD_NAMES, metavar="FOOD_NAME")
@click.option("--amount", default=1, type=valid_feeding_amount,
              metavar="N_FOOD",
              help="number of FOOD_NAME fed to PET_NAME")
def feed(pet_name: str, food_name: str, amount: int):
    """feed a pet

     \b
     PET_NAME   name of the pet (e.g. "Wolf-Golden")
     FOOD_NAME  name of the food (e.g. "Honey")

     \b
     Examples:
     ---
     # Feed a Beetle-Skeleton a Fish
     hopla feed pet Beetle-Skeleton Fish

     \b
     # Feed a Snail-Desert 5 Potatoes
     #   This fails to feed anything if less than 5 Potatoes are
     #   required for a pet to become a mount.
     hopla feed --amount=5 Snail-Desert Potatoe

     [API-docs](https://habitica.com/apidoc/#api-User-UserFeed)
    \f
    :return:

    Note: this API endpoint expect 'amount' as a query params (?amount=N) instead
    of a request body (even though it is a HTTP POST).
    """
    log.debug(f"hopla feed pet={pet_name}, food={food_name}")
    pet_feed_request = PetFeedPostRequester(
        pet_name=pet_name,
        food_name=food_name,
        food_amount=amount
    )

    response = pet_feed_request.post_feed_pet_food_request()
    feed_data = data_on_success_else_exit(response)

    click.echo(JsonFormatter(feed_data).format_with_double_quotes())
    return feed_data
