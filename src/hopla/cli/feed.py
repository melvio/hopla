"""
The module with CLI code that handles the `hopla feed` command.
"""
import logging
import sys

import click
import requests

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.hoplalib.zoo.petmodels import InvalidPet, Pet
from hopla.hoplalib.zoo.petcontroller import FeedPostRequester
from hopla.hoplalib.zoo.petdata import PetData

log = logging.getLogger()

valid_feed_amount_range = click.IntRange(min=0, max=23, clamp=True)
"""pets can eat up to 23 units of non-preferred foods"""


def print_favorite_food_and_exit(pet_name: str):
    """Print favorite food for the specified pet and always exit."""
    pet = Pet(pet_name)
    click.echo(pet.favorite_food())
    sys.exit()


def get_favorite_food_or_exit(pet_name: str):
    """Get the favorite food for the specified pet, else exit with 1."""
    try:
        pet = Pet(pet_name=pet_name)
        favorite_food = pet.favorite_food()
    except (InvalidPet, ValueError) as ex:
        click.echo(f"We could not create {pet_name}. Received the following exception:")
        click.echo(ex)
        sys.exit(1)

    __exit_if_pet_has_no_favorite_food(pet_name, favorite_food)

    return favorite_food


def __exit_if_pet_has_no_favorite_food(pet_name: str, favorite_food: str):
    if favorite_food == "Any":
        msg = f"{pet_name} likes all foods. You must specify a FOOD_NAME for this pet."
        click.echo(msg)
        sys.exit(1)
    elif favorite_food == "Unfeedable":  # pragma: unreachable branch
        msg = f"{pet_name} is a special pet. It cannot be fed."
        click.echo(msg)
        sys.exit(1)


def __get_feed_data_or_exit(feed_response: requests.Response):
    """
    Given a feed response, if the API request was successful, return interesting
    feeding information. On failure, exit with an error message.
    """
    response_json = feed_response.json()
    if response_json["success"]:
        feed_data = {"feeding_status": response_json["data"], "message": response_json["message"]}

        click.echo(JsonFormatter(feed_data).format_with_double_quotes())
        return feed_data

    click.echo(response_json["message"])
    sys.exit(feed_response.status_code)


@click.command()
@click.argument(
    "pet_name", type=click.Choice(PetData.feedable_pet_names),
    metavar="PET_NAME"
)
@click.argument(
    "food_name", type=click.Choice(PetData.drop_food_names),
    metavar="[FOOD_NAME]", required=False
)
@click.option(
    "--list-favorite-food/--no-list-favorite-food",
    default=False, show_default=True,
    help="Print favorite food for PET_NAME and exit."
)
@click.option(
    "--times", type=valid_feed_amount_range,
    metavar="N_FOOD",
    default=1, show_default=True,
    help=
    "Number of FOOD_NAME to feed to PET_NAME.\n "
    f"Values under {valid_feed_amount_range.min} are clamped to {valid_feed_amount_range.min}. "
    f"Values over {valid_feed_amount_range.max} are clamped to {valid_feed_amount_range.max}."
)
def feed(pet_name: str, food_name: str,
         list_favorite_food: bool,
         times: int):
    """Feed a pet.

     \b
     PET_NAME   name of the pet (e.g. "Wolf-Golden")
     FOOD_NAME  name of the food (e.g. "Honey").

     \b
     Examples:
     ---
     # Feed a Beetle-Skeleton a Fish
     $ hopla feed Beetle-Skeleton Fish

     \b
     # Feed a Snail-Desert 5 Potatoes
     # This commands fails to feed anything if less than 5 Potatoes are
     # required for a pet to become a mount.
     $ hopla feed --times=5 Snail-Desert Potatoe

     \b
     # List a pet's favorite food
     $ hopla feed Axolotl-Base --list-favorite-food
     Meat

     \b
     # Tip: You can use the <Tab> key to show the pet and food keys
     $ hopla feed <Tab><Tab>
     $ hopla feed Axolotl-White <Tab><Tab>

     [API-docs](https://habitica.com/apidoc/#api-User-UserFeed)
    \f
    :return:

    Note: this API endpoint expect 'amount' as a query params (?amount=N) instead
    of a request body (even though it is a HTTP POST).
    """
    log.debug(f"hopla feed {pet_name=}, {food_name=}"
              f" {times=} "
              f" {list_favorite_food=}")

    if list_favorite_food:
        print_favorite_food_and_exit(pet_name=pet_name)

    if food_name is None:
        food_name = get_favorite_food_or_exit(pet_name=pet_name)
        log.debug(f"Favorite food is automatically selected to be {food_name=}.")

    pet_feed_request = FeedPostRequester(
        pet_name=pet_name,
        food_name=food_name,
        food_amount=times
    )

    response: requests.Response = pet_feed_request.post_feed_request()
    return __get_feed_data_or_exit(feed_response=response)
