"""
A helper module for Pet logic.
"""
from dataclasses import dataclass
from typing import Optional

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.errors import PrintableException, YouFoundABugRewardError
from hopla.hoplalib.hatchery.hatchpotion_data import HatchPotionData
from hopla.hoplalib.zoo.fooddata import FoodData
from hopla.hoplalib.zoo.foodmodels import FeedStatus
from hopla.hoplalib.zoo.petdata import PetData


class InvalidPet(PrintableException):
    """Exception raised when a pet is invalid."""

    def __init__(self, msg: str, *, pet: Optional["Pet"] = None):
        super().__init__(msg)
        self.pet = pet


@dataclass
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
                 feed_status: FeedStatus = FeedStatus(5)):
        if pet_name not in PetData.pet_names:
            raise InvalidPet(f"{pet_name=} is not recognized by hopla.\n"
                             "Potential causes: \n"
                             "* did you spell it correctly?\n"
                             "* Is your pet relatively new? If so, please raise\n"
                             f" an issue at {GlobalConstants.NEW_ISSUE_URL}")

        self.name = pet_name
        self.feed_status = feed_status

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}: {self.feed_status})"

    @property
    def hatch_potion_name(self) -> Optional[str]:
        """The hatching potion used to hatch the egg this pet came from."""
        if self.name in PetData.rare_pet_names:
            return None

        # This logic might break, but seems to be solid for past few years due to
        # stabling naming convention by the Habitica API developers.
        _, potion = self.name.split("-")
        return potion

    def is_available(self) -> bool:
        """Return True if the feed status says that the pet is available."""
        return self.feed_status.is_pet_available()

    def is_feedable(self) -> bool:
        """Return True if a pet cannot be fed at all."""
        return self.name not in PetData.unfeedable_pet_names

    def has_just_1_favorite_food(self) -> bool:
        """Return True if this pet likes only 1 type of food."""
        return self.name in PetData.only_1favorite_food_pet_names

    def likes_all_food(self) -> bool:
        """Return True if this pet prefers all food."""
        return self.name in PetData.magic_potion_pet_names

    def feed_status_explanation(self) -> str:
        """Explain the feed status of a pet."""
        if self.is_feedable() is False:
            return f"{self.name} is an unfeedable pet."
        if int(self.feed_status) == 0:
            return f"You released {self.name}, so you cannot feed it."

        if int(self.feed_status) == -1:
            return f"You can't feed {self.name=} you only have the mount"

        if int(self.feed_status) == 5:
            # remark: if we really want to know more, we can query the
            #         API to check if we have the self.name in the
            #         Users: jq .data.items.mounts
            return (f"Cannot determine if {self.name=} can be fed. \n"
                    "You either have:\n"
                    "1. Both the pet and mount. In this case, you cannot feed the pet \n"
                    "2. A pet that hasn't been fed but you don't have \n"
                    "   the mount. In this case, you can feed your pet")

        if int(self.feed_status) < 50:
            return f"{self.name=} can be fed"

        raise InvalidPet(f"Did not expect {self.feed_status=}. \n"
                         f"Looks like we failed to validate the Pet properly.",
                         pet=self)  # pragma: no cover

    def favorite_food(self, *,
                      default_value_for_unfeedable: str = "Unfeedable",
                      default_value_for_all_favorite_food: str = "Any") -> str:
        """Return the favorite food of this pet."""
        if self.is_feedable() is False:
            return default_value_for_unfeedable

        if self.name in PetData.magic_potion_pet_names:
            return default_value_for_all_favorite_food

        if self.has_just_1_favorite_food():
            return (FoodData.hatch_potion_favorite_food_mapping
                    .get(self.hatch_potion_name))

        raise InvalidPet(f"Could not find the feed habits of this {self.name=}",
                         pet=self)  # pragma: no cover

    def is_favorite_food(self, food_name: str) -> bool:
        """Return true if 'food_name' is this Pets favorite food."""
        if self.is_feedable() is False:
            return False
        if self.likes_all_food():
            return True
        if self.has_just_1_favorite_food():
            return self.favorite_food() == food_name

        raise InvalidPet(f"Unable to determine if {food_name=} is {self.name=}'s favorite.",
                         pet=self)  # pragma: no cover

    def required_food_items_until_mount(self, food_name: str) -> int:
        """
        Return the number of times food_name needs to be fed
        for this pet to turn into a mount
        """
        is_favorite: bool = self.is_favorite_food(food_name)
        return self.feed_status.required_food_items_to_become_mount(is_favorite)

    def is_generation1_pet(self) -> bool:
        """Return True if this pet is from the generation 1 pet"""
        return self.name in PetData.generation1_pet_names

    def is_quest_pet(self) -> bool:
        """
        Return True if this pet is a quest pet. This doesn't include
        special pets such as world event related pets.
        """
        return self.name in PetData.quest_pet_names

    def is_magic_hatch_pet(self) -> bool:
        """Return True if this pet is hatched from a magic potion."""
        return self.name in PetData.magic_potion_pet_names

    def is_from_drop_hatch_potions(self) -> bool:
        """
        Return True if the pet was hatched from one of the 'ordinary'
        potions. (Such as: Base, Desert, ...).
        """
        return self.hatch_potion_name in HatchPotionData.drop_hatch_potion_names


@dataclass
class Mount:
    """ The model class for mounts."""

    def __init__(self, mount_name: str, *,
                 availability_status: Optional[bool]):
        """
        Create a mount.

        Note that, in contrast to Pet.__init__, currently, there is no name
        correctness checking. Related ticket:
        https://github.com/melvio/hopla/issues/164

        :param mount_name:
        :param availability_status:
        """
        self.name = mount_name
        self._availability_status = availability_status

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}: {self._availability_status})"

    def is_available(self) -> bool:
        """Return true if the user has the mount right now."""
        return self._availability_status is True


class InvalidPetMountPair(YouFoundABugRewardError):
    """Exception raised when an invalid PetMountPair is created."""


@dataclass
class PetMountPair:
    """A pair of a pet and its mount."""

    def __init__(self, *, pet: Optional[Pet],
                 mount: Optional[Mount]):
        """
        Create a PetMountPair.
        Raise an exception if the names of the pet and mount do not match.
        """
        if pet and mount:
            if pet.name != mount.name:
                msg = f"pet name '{pet.name}' must equal mount name '{mount.name}'"
                raise InvalidPetMountPair(msg)

        self.pet = pet
        self.mount = mount

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pet={self.pet}, mount={self.mount})"

    def can_feed_pet(self) -> bool:
        """Return true if the pet itself is feedable and there is no mount yet."""
        return (
                self.pet_available()
                and self.pet.is_feedable()
                and not self.mount_available()
        )

    def mount_available(self) -> bool:
        """True if the mount is in the pair"""
        return self.mount is not None and self.mount.is_available()

    def pet_available(self) -> bool:
        """True if the pet is in the pair"""
        return self.pet is not None and self.pet.is_available()
