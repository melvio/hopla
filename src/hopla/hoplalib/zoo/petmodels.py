"""
A helper module for Pet logic.
"""
from dataclasses import dataclass
from typing import Callable, Dict, NoReturn, Optional

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.errors import PrintableException
from hopla.hoplalib.zoo.fooddata import FoodData
from hopla.hoplalib.zoo.foodmodels import FeedingStatus, InvalidFeedingStatus
from hopla.hoplalib.zoo.petdata import PetData


class InvalidPet(PrintableException):
    """Exception raised when a pet is invalid."""

    def __init__(self, msg: str, *, pet: Optional["Pet"] = None):
        super().__init__(msg)
        self.pet = pet


class Pet:
    """A habitica pet"""

    # pylint: disable=too-many-public-methods
    #################################################################
    # In a way, pylint is right. This class does have a lot of functions.
    # Most of these are oneliners, however we can also use polymorphism.
    # That would make it easier to find functions in this class.
    # We can use a PetFactory that creates QuestPets, MagicPets etc.
    # However, that is really overkill for now and not urgent enough.
    # Therefore, too-many-public-methods is disabled for this class.
    #################################################################

    def __init__(self, pet_name: str, *,
                 feeding_status: FeedingStatus = FeedingStatus(5)):
        if pet_name not in PetData.pet_names:
            raise InvalidPet(f"{pet_name=} is not recognized by hopla.\n"
                             "Potential causes: \n"
                             "* did you spell it correctly?\n"
                             "* Is your pet relatively new? If so, please raise\n"
                             f" an issue at {GlobalConstants.NEW_ISSUE_URL}")

        self.pet_name = pet_name
        self.feeding_status = feeding_status

        if pet_name in PetData.rare_pet_names:
            self.__potion = None
        else:
            # This logic might break, but seems to be solid for past few years due to
            # stabling naming convention by the Habitica API developers.
            _, self.__potion = self.pet_name.split("-")

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.pet_name=}, {self.feeding_status=})"

    @property
    def hatching_potion(self):
        """The hatching potion used to hatch the egg this pet came from."""
        return self.__potion

    def is_feedable(self) -> bool:
        """Return True if a pet cannot be fed at all."""
        return self.pet_name not in PetData.unfeedable_pet_names

    def has_just_1_favorite_food(self) -> bool:
        """Return True if this pet likes only 1 type of food."""
        return self.pet_name in PetData.only_1favorite_food_pet_names

    def likes_all_food(self) -> bool:
        """Return True if this pet prefers all food."""
        return self.pet_name in PetData.magic_potion_pet_names

    def feeding_status_explanation(self) -> str:
        """Explain the feeding status of a pet."""
        if self.is_feedable() is False:
            return f"{self.pet_name=} can't be fed because it is special."
        if int(self.feeding_status) == -1:
            return f"You can't feed {self.pet_name=} you only have the mount"

        if int(self.feeding_status) == 5:
            # remark: if we really want to know more, we can query the
            #         API to check if we have the self.pet_name in the
            #         Users: jq .data.items.mounts
            return (f"Cannot determine if {self.pet_name=} can be fed. \n"
                    "You either have:\n"
                    "1. Both the pet and mount. In this case, you"
                    "   cannot feed the pet \n"
                    "2. A pet that hasn't been fed but you don't have \n"
                    "   the mount. In this case, you can feed your pet")

        if int(self.feeding_status) < 50:
            return f"{self.pet_name=} can be fed"

        raise InvalidPet(f"Did not expect {self.feeding_status=}. \n"
                         f"Looks like we failed to validate the Pet properly.",
                         pet=self)  # pragma: no cover

    def favorite_food(self, *,
                      default_value_for_unfeedable: str = "Unfeedable",
                      default_value_for_all_favorite_food: str = "Any") -> str:
        """Return the favorite food of this pet."""
        if self.is_feedable() is False:
            return default_value_for_unfeedable

        if self.pet_name in PetData.magic_potion_pet_names:
            return default_value_for_all_favorite_food

        if self.has_just_1_favorite_food():
            return (FoodData.hatching_potion_favorite_food_mapping
                    .get(self.hatching_potion))

        raise InvalidPet(f"Could not find the feeding habits of this {self.pet_name=}",
                         pet=self)  # pragma: no cover

    def is_favorite_food(self, food_name: str) -> bool:
        """Return true if 'food_name' is this Pets favorite food."""
        if self.is_feedable() is False:
            return False
        if self.likes_all_food():
            return True
        if self.has_just_1_favorite_food():
            return self.favorite_food() == food_name

        raise InvalidPet(f"Unable to determine if {food_name=} is {self.pet_name=}'s favorite.",
                         pet=self)  # pragma: no cover

    def required_food_items_until_mount(self, food_name: str) -> int:
        """
        Return the number of times food_name needs to be fed
        for this pet to turn into a mount
        """
        is_favorite: bool = self.is_favorite_food(food_name)
        return self.feeding_status.required_food_items_to_become_mount(is_favorite)

    def is_generation1_pet(self) -> bool:
        """Return True if this pet is from the generation 1 pet"""
        return self.pet_name in PetData.generation1_pet_names

    def is_quest_pet(self) -> bool:
        """
        Return True if this pet is a quest pet. This doesn't include
        special pets such as world event related pets.
        """
        return self.pet_name in PetData.quest_pet_names

    def is_magic_hatching_pet(self) -> bool:
        """Return True if this pet is hatched from a magic potion."""
        return self.pet_name in PetData.magic_potion_pet_names

    def is_from_drop_hatching_potions(self) -> bool:
        """
        Return True if the pet was hatched from one of the 'ordinary'
        potions. (Such as: Base, Desert, ...).
        """
        return self.hatching_potion in FoodData.drop_hatching_potions


class PetMountPair:
    """A pair of a pet and its corresponding mount information."""

    def __init__(self, pet: Pet, *,
                 pet_available: bool,
                 mount_available: bool):
        """Create a Pet-Mount pair"""
        if pet.feeding_status is None:
            msg = f"PetMountPair requires that {pet=} has a feeding status"
            raise InvalidFeedingStatus(msg)

        self.pet = pet
        self.pet_available = pet_available
        self.mount_available = mount_available

    def __repr__(self):
        return self.__class__.__name__ + f"({self.__dict__})"

    def can_feed_pet(self) -> True:
        """Return true if the pet itself is feedable and there is no mount yet."""
        return (
                self.mount_available is False
                and self.pet_available
                and self.pet.is_feedable()
                and int(self.pet.feeding_status) != -1
        )


Zoo = Dict[str, PetMountPair]
"""
Zoo is dictionary with key pet name keys for O(1) access to the
PetMountPair.
"""


@dataclass(frozen=True)
class ZooHelper:
    """Class with helper functions for a Zoo."""
    zoo: Zoo

    def filter_on_pet_mount_pairs(self, predicate: Callable[[PetMountPair], bool]) -> Zoo:
        """Filter the zoo on the pair. This does not change the underlying zoo.

        :param predicate: Include the PetMountPair if the predicate returns True, else
                          omit the pair.
        :return: A filtered Zoo
        """
        return {
            pet_name: pair for (pet_name, pair) in self.zoo.items() if predicate(pair)
        }

    def get_feedable_zoo(self) -> Zoo:
        """Helper function to get only the pets that can be fed in this Zoo."""
        return self.filter_on_pet_mount_pairs(PetMountPair.can_feed_pet)

    def filter_on_pet_name(self, predicate: Callable[[str], bool]) -> Zoo:
        """Filter the zoo on the pet name. This does not change the underlying zoo.

        :param predicate: Include the PetMountPair if the predicate returns True, else
                          omit the pair.
        :return: A filtered zoo.
        """
        return {
            pet_name: pair for (pet_name, pair) in self.zoo.items() if predicate(pet_name)
        }

    def filter_on_pet(self, predicate: Callable[[Pet], bool]) -> Zoo:
        """Filter the zoo on the pet object. This does not change the underlying zoo.

        :param predicate: Include the PetMountPair if the predicate returns True, else
                          omit the pair.
        :return: A filtered zoo.
        """
        return {
            pet_name: pair for (pet_name, pair) in self.zoo.items() if predicate(pair.pet)
        }


class ZooBuilder:
    """
    Class that creates a Zoo from a HabiticaUser using the
    builder design pattern.
    """

    def __init__(self, user: HabiticaUser):
        self.pets: dict = user.get_pets()
        self.mounts: dict = user.get_mounts()
        self.__zoo: Zoo = {}  # empty until build() is called

    def __repr__(self):
        return self.__class__.__name__ + f"({self.__dict__})"

    def build(self) -> Zoo:
        """Create the Zoo. Return the Zoo in case of success"""
        self.__build()
        return self.__zoo

    def __build(self) -> NoReturn:
        self.__add_pets_to_zoo()
        self.__add_remaining_mounts_to_zoo()

    def __add_pets_to_zoo(self) -> NoReturn:
        for pet_name in self.pets:
            feed_status = self.pets[pet_name]
            if self.mounts.get(pet_name) is None:
                mount_available = False
            else:
                mount_available = True
                del self.mounts[pet_name]  # found the mount!

            pet_available = feed_status != -1
            pet = Pet(pet_name, feeding_status=FeedingStatus(feed_status))
            pair = PetMountPair(pet,
                                pet_available=pet_available,
                                mount_available=mount_available)

            self.__zoo[pet_name] = pair

    def __add_remaining_mounts_to_zoo(self) -> NoReturn:
        for mount_name in self.mounts:
            # Watch out: we are abusing the Pet object for mount only animals here
            pet = Pet(mount_name)

            pair = PetMountPair(pet,
                                pet_available=False,
                                mount_available=True)
            self.__zoo[mount_name] = pair
