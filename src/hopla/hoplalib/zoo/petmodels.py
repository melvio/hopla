"""
A helper module for Pet logic.
"""
import math
from hopla.hoplalib.clickhelper import PrintableException

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.zoo.petdata import PetData


class InvalidPet(PrintableException):
    """Exception raised when a pet is invalid."""

    def __init__(self, msg: str, *, pet=None):
        super().__init__(msg)
        self.pet = pet


class InvalidFeedingStatus(PrintableException):
    """Exception raised when a pet is invalid."""

    def __init__(self, msg: str, *, pet=None):
        super().__init__(msg)
        self.pet = pet


class FeedingStatus:
    """A class implementing feeding status logic for pets"""
    START_FEEDING_STATE = 5
    FULLY_FED_STATE = 50
    FAVORITE_INCREMENT = 5
    NON_FAVORITE_INCREMENT = 2

    def __init__(self, feeding_status: int = START_FEEDING_STATE):
        # every pet starts at 5
        # 50 would turn the pet into a mount
        # The feeding status of 0 is documented but never returned anno Sept 2021
        valid_status = (feeding_status < -1
                        or feeding_status in [1, 2, 3, 4]
                        or feeding_status >= 50)
        if valid_status:
            raise InvalidFeedingStatus(f"{feeding_status=} is invalid")

        self.feeding_status = feeding_status

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.feeding_status})"

    def __int__(self) -> int:
        return self.feeding_status

    def required_food_items_to_become_mount(self, is_favorite_food: bool) -> int:
        """Return how many items of food we need to give to turn a pet into a mount."""
        target = FeedingStatus.FULLY_FED_STATE - self.feeding_status
        if is_favorite_food:
            required_food = math.ceil(target / FeedingStatus.FAVORITE_INCREMENT)
        else:
            required_food = math.ceil(target / FeedingStatus.NON_FAVORITE_INCREMENT)
        return required_food

    def to_percentage(self) -> int:
        """
        Turn feeding status into percentage understandable by the
        website user.
        <https://habitica.fandom.com/wiki/Food_Preferences>
        """
        if self.feeding_status == -1:
            return 100  # The pet is now a mount
        return self.feeding_status * 2


class Pet:
    """A habitica pet"""

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
        """Return True if pet likes only 1 type of food"""
        return self.pet_name in PetData.only_1favorite_food_pet_names

    def likes_all_food(self) -> bool:
        """Return True if this prefers all food."""
        return self.pet_name in PetData.magic_potion_pet_names

    def feeding_status_explanation(self) -> str:
        """Explain the feeding status of a pet"""
        if self.is_feedable() is False:
            return f"{self.pet_name=} can't be fed because it is special."
        if self.feeding_status.feeding_status == -1:
            return f"You can't feed {self.pet_name=} you only have the mount"

        if self.feeding_status.feeding_status == 5:
            # remark: if we really want to know more, we can query the
            #         API to check if we have the self.pet_name in the
            #         Users: jq .data.items.mounts
            return (f"Cannot determine if {self.pet_name=} can be fed. \n"
                    "You either have:\n"
                    "1. both the pet and mount: You cannot feed the pet \n"
                    "2. a pet that hasn't been fed but you don't have \n"
                    "   the mount: You can feed your pet")

        if self.feeding_status.feeding_status < 50:
            return f"{self.pet_name=} can be fed"

        raise InvalidPet(f"Did not expect {self.feeding_status.feeding_status=}. \n"
                         f"Looks like we failed to validate the Pet properly.",
                         pet=self)  # pragma: no cover

    def favorite_food(self, *,
                      default_value_for_unfeedable: str = "Unfeedable",
                      default_value_for_all_favorite_food: str = "Any"):
        """Return the favorite food of this pet."""
        if self.is_feedable() is False:
            return default_value_for_unfeedable

        if self.pet_name in PetData.magic_potion_pet_names:
            return default_value_for_all_favorite_food

        if self.has_just_1_favorite_food():
            return (PetData.hatching_potion_favorite_food_mapping
                    .get(self.hatching_potion))

        raise InvalidPet(f"Could not find the feeding habits of this {self.pet_name=}",
                         pet=self)  # pragma: no cover

    def is_favorite_food(self, food_name: str) -> bool:
        """Return true if 'food_name' is this Pets favorite food. """
        if self.is_feedable() is False:
            return False
        if self.likes_all_food():
            return True
        if self.has_just_1_favorite_food():
            return self.favorite_food() == food_name

        raise InvalidPet(f"Unable to determine if {food_name=} is {self.pet_name=}'s favorite.",
                         pet=self)  # pragma: no cover

    def is_generation1_pet(self) -> bool:
        """Return True if this pet is from the generation 1 pet"""
        return self.pet_name in PetData.generation1_pet_names

    def is_from_drop_hatching_potions(self) -> bool:
        """
        Return True if the pet was hatched from one of the 'ordinary'
        potions. (Such as: Base, Desert, ...).
        """
        return self.hatching_potion in PetData.drop_hatching_potions


class PetMountPair:
    """A pair of a pet and its corresponding mount information"""

    def __init__(self, pet: Pet, mount_available: bool):
        """Create a Pet-Mount pair"""
        if pet.feeding_status is None:
            raise InvalidPet(f"PetMountPair requires that {pet=} has a feeding status")

        self.pet = pet
        self.mount_available = mount_available

    def can_feed_pet(self) -> True:
        """Return true if the pet itself is feedable and there is no mount yet."""
        return self.mount_available is False and self.pet.is_feedable()
