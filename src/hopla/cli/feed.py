"""
The module with CLI code that handles the `hopla feed` command.
"""
import logging
import sys
from typing import NoReturn, Optional, Union

import click
import requests

from hopla.cli.groupcmds.get_user import HabiticaUser, HabiticaUserRequest
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.hoplalib.zoo.petmodels import InvalidPet, Pet
from hopla.hoplalib.zoo.petmodels import PetMountPair, Zoo, ZooBuilder
from hopla.hoplalib.zoo.petcontroller import FeedPostRequester
from hopla.hoplalib.zoo.petdata import PetData

log = logging.getLogger()

MIN_FEED_TIMES = 0
MAX_FEED_TIMES = 23
valid_feed_amount_range = click.IntRange(min=MIN_FEED_TIMES,
                                         max=MAX_FEED_TIMES,
                                         clamp=True)
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


__TIMES_OPTION = "--times"
__UNTIL_MOUNT_OPTION = "--until-mount"


def get_feed_times_until_mount(pet_name: str, food_name: str) -> Union[int, NoReturn]:
    """
    Return how often a pet needs to be fed until it turns into a mount.

    :param pet_name: the pet to be fed
    :param food_name: the food to give the pet
    :return: times to feed, or exit if feeding this pet is not possible.
    """
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    zoo: Zoo = ZooBuilder(user).build()
    pair: PetMountPair = zoo.get(pet_name)
    if pair is None:
        sys.exit(f"Can't feed pet {pet_name}. You don't have this pet.")
    if pair.mount_available:
        sys.exit(f"Can't feed pet {pet_name}. You have the mount.")

    pet: Pet = pair.pet
    if pair.can_feed_pet() is False:
        sys.exit(f"Can't feed pet {pet_name}. "
                 + pet.feeding_status_explanation())

    return pet.required_food_items_until_mount(food_name)


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
    __TIMES_OPTION, type=valid_feed_amount_range,
    metavar="N_FOOD",
    help="Number of FOOD_NAME to feed to PET_NAME.\n "
         f"Values under {MIN_FEED_TIMES} are clamped to {MIN_FEED_TIMES}. "
         f"Values over {MAX_FEED_TIMES} are clamped to {MAX_FEED_TIMES}."
)
@click.option(
    f"{__UNTIL_MOUNT_OPTION}/--no-until-mount",
    default=False, show_default=True,
    help="Keep feeding this pet until it is a mount.")
@click.option(
    "--list-favorite-food/--no-list-favorite-food",
    default=False, show_default=True,
    help="Print favorite food for PET_NAME and exit."
)
def feed(pet_name: str, food_name: str,
         times: int, until_mount: bool,
         list_favorite_food: bool):
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
     # Feed a pet its favorite food once. This only works if a pet
     # pet is feedable and has one favorite food.
     $ hopla feed Rock-White

     \b
     # Feed a pet its favorite food until it is a mount. This
     # only works if a pet is feedable and has one favorite food.
     $ hopla feed TRex-Red --until-mount

     \b
     # Feed a pet a specific type of food until it is a mount. This
     # commands also work with pets that like all foods. (e.g. pets
     # hatched with magic hatching potions.)
     $ hopla feed --until-mount Wolf-SandSculpture RottenMeat

     \b
     # Feed a Snail-Desert 5 Potatoes. Note that this commands fails
     # to feed anything if fewer than 5 Potatoes are required
     # for a pet to become a mount. It also fails if you don't have
     # this pet, or not enough potatoes.
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
              f" {times=} {until_mount=}"
              f" {list_favorite_food=}")

    __raise_if_conflicting(times=times, until_mount=until_mount)

    if list_favorite_food:
        print_favorite_food_and_exit(pet_name=pet_name)

    if food_name is None:
        food_name = get_favorite_food_or_exit(pet_name=pet_name)
        log.debug(f"Favorite food is automatically selected to be {food_name=}.")

    if until_mount:
        times: int = get_feed_times_until_mount(pet_name=pet_name,
                                                food_name=food_name)

    pet_feed_request = FeedPostRequester(
        pet_name=pet_name,
        food_name=food_name,
        food_amount=times
    )

    response: requests.Response = pet_feed_request.post_feed_request()
    return __get_feed_data_or_exit(feed_response=response)


def __raise_if_conflicting(*, times: Optional[int], until_mount: bool):
    if until_mount and times is not None:
        raise click.UsageError(
            "Conflicting options: "
            f"Cannot specify both {__TIMES_OPTION} and {__UNTIL_MOUNT_OPTION}."
        )
