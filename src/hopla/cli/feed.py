"""
The module with CLI code that handles the `hopla feed` command.
"""
import logging

import click
import requests

from hopla.hoplalib.clickutils import data_on_success_else_exit
from hopla.hoplalib.http import RequestHeaders, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


class PetFeedPostRequester:
    """
    The PetFeedPostRequester sends a post request to feed a pet.

    Note: this API endpoint expects query params instead
    of a request body (even though it is a HTTP POST).

    [APIDOCS](https://habitica.com/apidoc/#api-User-UserFeed)
    """

    def __init__(self, *,
                 request_headers: dict,
                 pet_name: str,
                 food_name: str,
                 food_amount: int = 1):
        self.request_headers = request_headers
        self.pet_name = pet_name
        self.food_name = food_name
        self.query_params = {"amount": food_amount}

    @property
    def path(self) -> str:
        """Return the URL used to feed a pet"""
        return f"/user/feed/{self.pet_name}/{self.food_name}"

    @property
    def feed_pet_food_url(self) -> str:
        return UrlBuilder(path_extension=self.path).url

    def post_feed_pet_food(self) -> requests.Response:
        return requests.post(
            url=self.feed_pet_food_url,
            headers=self.request_headers,
            params=self.query_params
        )


# pets can eat up to 50 units of non-preferred foods
# TODO: Not sure if, want to clamp=True (which results
#  in 100 automatically becomes max, -10 becomes min, instead of failing
#   with an click validation error message)
# * Look into other options first, such as; --until-mount
valid_feeding_amount = click.IntRange(min=0, max=50, clamp=False)


@click.command()
@click.argument("pet_name")
@click.argument("food_name")
@click.option("--amount",
              default=1, show_default=True,
              type=valid_feeding_amount,
              metavar="N_FOOD", help="number of FOOD_NAME fed to PET_NAME"
              )
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
     # Feed a Snail-Desert 5 Potatoe
     #   This fails to feed anything if less than 5 Potatoes are
     #   required for a pet to become a mount
     hopla feed --amount=5 Snail-Desert Potatoe



     [API-docs](https://habitica.com/apidoc/#api-User-UserFeed)
    \f
    :return:

    Note: this API endpoint expect 'amount' as a query params (?amount=N) instead
    of a request body (even though it is a HTTP POST).
    """
    log.debug("hopla feed ")
    headers = RequestHeaders().get_default_request_headers()
    pet_feed_request = PetFeedPostRequester(
        request_headers=headers,
        pet_name=pet_name,
        food_name=food_name,
        food_amount=amount
    )

    response = pet_feed_request.post_feed_pet_food()
    feed_data = data_on_success_else_exit(response)

    click.echo(JsonFormatter(feed_data).format_with_double_quotes())
