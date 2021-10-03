"""
The module with CLI code that handles the `hopla feed` command.
"""
import logging
import sys
from dataclasses import dataclass
from typing import NoReturn, Optional, Union

import click
import requests

from hopla.cli.groupcmds.get_user import HabiticaUser, HabiticaUserRequest
from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.zoo.feed_clickhelper import get_feed_data_or_exit
from hopla.hoplalib.zoo.fooddata import FoodData
from hopla.hoplalib.zoo.foodmodels import FoodStockpile, FoodStockpileBuilder
from hopla.hoplalib.zoo.petcontroller import FeedPostRequester
from hopla.hoplalib.zoo.petdata import PetData
from hopla.hoplalib.zoo.petmodels import Pet, PetMountPair
from hopla.hoplalib.zoo.zoomodels import Zoo, ZooBuilder

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
    if pair is None or pair.pet_available() is False:
        sys.exit(f"Can't feed pet {pet_name}. You don't have this pet.")
    if pair.mount_available():
        sys.exit(f"Can't feed pet {pet_name}. You have the mount.")

    pet: Pet = pair.pet
    if pair.can_feed_pet() is False:
        sys.exit(f"Can't feed pet {pet_name}. "
                 + pet.feed_status_explanation())

    return pet.required_food_items_until_mount(food_name)


def get_appropriate_food_or_exit(pet_name: str) -> Union[str, NoReturn]:
    """Return the food that is appropriate for this pet.

    For pets hatched with normal hatching potion, return their favorite food.
    For pets hatched with magic hatching potion, return the most abundant food you have.
    Other types of pets should not be received by this function.
    """
    pet = Pet(pet_name)
    if pet.has_just_1_favorite_food():
        return pet.favorite_food()

    if pet.likes_all_food():
        user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
        stockpile: FoodStockpile = FoodStockpileBuilder().user(user).build()
        return stockpile.get_most_abundant_food()

    # This should be unreachable if we configured click with the correct pets.
    msg = (f"We tried to find the appropriate food for {pet_name=}.\n"
           "We assumed that we would have found the appropriate food by now.\n"
           "Unfortunately, that was not the case.")
    raise YouFoundABugRewardError(msg)


_TIMES_OPTION = "--times"
_UNTIL_MOUNT_OPTION = "--until-mount"


@click.command()
@click.argument(
    "pet_name", type=click.Choice(PetData.feedable_pet_names),
    metavar="PET_NAME"
)
@click.argument(
    "food_name", type=click.Choice(FoodData.drop_food_names),
    metavar="[FOOD_NAME]", required=False
)
@click.option(
    _TIMES_OPTION, type=valid_feed_amount_range,
    metavar="N_FOOD",
    help="Number of FOOD_NAME to feed to PET_NAME.\n "
         f"Values under {MIN_FEED_TIMES} are clamped to {MIN_FEED_TIMES}. "
         f"Values over {MAX_FEED_TIMES} are clamped to {MAX_FEED_TIMES}."
)
@click.option(
    f"{_UNTIL_MOUNT_OPTION}/--no-until-mount",
    default=False, show_default=True,
    help="Keep feeding this pet until it is a mount."
)
@click.option(
    "--list-favorite-food/--no-list-favorite-food",
    default=False, show_default=True,
    help="Print favorite food for PET_NAME and exit."
)
def feed(pet_name: str, food_name: str,
         times: int, until_mount: bool,
         list_favorite_food: bool):
    """Feed a single pet.

     \b
     PET_NAME   name of the pet (e.g. Wolf-Golden)
     FOOD_NAME  name of the food (e.g. Honey).

     \b
     Examples:
     ---
     # Feed a Beetle-Skeleton a Fish
     $ hopla feed Beetle-Skeleton Fish

     \b
     # Feed a pet its favorite food once. This only works if a pet
     # pet is feedable. For magic hatched pets, the most
     # abundant food you have is used.
     $ hopla feed Rock-White

     \b
     # Feed a pet its favorite food until it is a mount. This
     # only works if a pet is feedable.
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
     $ hopla feed Axolotl-White Milk

     [API-docs](https://habitica.com/apidoc/#api-User-UserFeed)
    \f
    :return:

    Note: this API endpoint expect 'amount' as a query params (?amount=N) instead
    of a request body (even though it is a HTTP POST).
    """
    log.debug(f"hopla feed {pet_name=}, {food_name=}"
              f" {times=} {until_mount=}"
              f" {list_favorite_food=}")

    FeedCommandParameterChecker(times=times, until_mount=until_mount) \
        .raise_if_conflicting_feed_time_options()

    if list_favorite_food:
        print_favorite_food_and_exit(pet_name=pet_name)

    if food_name is None:
        food_name = get_appropriate_food_or_exit(pet_name=pet_name)
        log.debug(f"Food is automatically selected to be {food_name=}.")

    if until_mount:
        times: int = get_feed_times_until_mount(pet_name=pet_name,
                                                food_name=food_name)
    else:
        times: int = times or 1

    pet_feed_request = FeedPostRequester(
        pet_name=pet_name,
        food_name=food_name,
        food_amount=times
    )

    response: requests.Response = pet_feed_request.post_feed_request()
    return get_feed_data_or_exit(feed_response=response)


@dataclass
class FeedCommandParameterChecker:
    """
    A class that raises errors when `hopla feed` received an invalid
    combination of parameters.
    """
    times: Optional[int]
    until_mount: bool

    def raise_if_conflicting_feed_time_options(self) -> Optional[NoReturn]:
        """
        The user should not use conflicting options that both specify
        how many food items should be given.
        """
        if self.until_mount and self.times is not None:
            raise click.UsageError(
                "Conflicting options: "
                f"Cannot specify both {_TIMES_OPTION} and {_UNTIL_MOUNT_OPTION}."
            )
