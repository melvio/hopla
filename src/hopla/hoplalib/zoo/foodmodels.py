"""
A helper module for feeding logic.
"""
import copy
import math
from dataclasses import dataclass
from typing import Dict, Final, Optional

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.errors import PrintableException
from hopla.hoplalib.zoo.fooddata import FoodData


class InvalidFeedStatus(PrintableException):
    """Exception raised when a pet is invalid."""

    def __init__(self, msg: str, *, pet=None):
        super().__init__(msg)
        self.pet = pet


class FeedStatus:
    """A class implementing feed status logic for pets.

    Every freshly hatched pet starts at 5.
    50 would turn the pet into a mount, so 50 is impossible to reach.
    The feed status of 0 means that you had the pet before, but
    you released it.
    """
    PET_GREW_UP_TO_MOUNT: Final[int] = -1
    PET_RELEASED: Final[int] = 0

    START_FEED_STATE: Final[int] = 5
    MAX_FED_STATE: Final[int] = 49
    FULLY_FED_STATE: Final[int] = 50

    FAVORITE_INCREMENT: Final[int] = 5
    NON_FAVORITE_INCREMENT: Final[int] = 2

    def __init__(self, feed_status: int = START_FEED_STATE):
        invalid_status = (feed_status < FeedStatus.PET_GREW_UP_TO_MOUNT
                          or feed_status in [1, 2, 3, 4]
                          or feed_status > FeedStatus.MAX_FED_STATE)
        if invalid_status:
            raise InvalidFeedStatus(f"{feed_status=} is invalid")

        self.__feed_status = feed_status

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__feed_status})"

    def __eq__(self, other):
        return isinstance(other, FeedStatus) and int(other) == int(self)

    def __hash__(self):
        return hash(self.__feed_status)

    def __int__(self) -> int:
        return self.__feed_status

    def is_pet_available(self):
        """Return True if the user currently has this pet."""
        return self.__feed_status not in [
            FeedStatus.PET_GREW_UP_TO_MOUNT, FeedStatus.PET_RELEASED
        ]

    def required_food_items_to_become_mount(self, is_favorite_food: bool) -> int:
        """Return how many items of food we need to give to turn a pet into a mount."""
        target = FeedStatus.FULLY_FED_STATE - self.__feed_status
        if is_favorite_food:
            required_food = math.ceil(target / FeedStatus.FAVORITE_INCREMENT)
        else:
            required_food = math.ceil(target / FeedStatus.NON_FAVORITE_INCREMENT)
        return required_food

    def to_percentage(self) -> int:
        """
        Turn feed status into percentage understandable by the
        website user.
        <https://habitica.fandom.com/wiki/Food_Preferences>
        """
        if self.__feed_status == -1:
            return 100  # The pet is now a mount
        return self.__feed_status * 2


class FoodException(PrintableException):
    """Exception thrown when there is a food error."""

    def __init__(self, msg: str, *, food: Optional["Food"] = None):
        super().__init__(msg)
        self.food = food


@dataclass(frozen=True)
class Food:
    """A stockpile food item."""
    name: str

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.name})"

    def is_rare_food_item(self) -> bool:
        """
        Return False if the food_item item is a drop food.
        Otherwise, return True.
        """
        return self.name not in FoodData.drop_food_names


@dataclass
class FoodStockpile:
    """The food of a user."""

    def __init__(self, __stockpile: Dict[str, int]):
        self.__stockpile = __stockpile

    def __eq__(self, other):
        # pylint: disable=protected-access
        return isinstance(other, FoodStockpile) and self.__stockpile == other.__stockpile

    def __hash__(self):
        return hash(self.__stockpile)

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.__stockpile})"

    def add_food(self, food_name: str, *, n: int) -> "FoodStockpile":
        """
        Change the number of specified food in the stockpile.

        :param food_name: the food to modify
        :param n: When n is positive, add this number of food.
                  When negative, subtract n from this food from the stockpile.
        :return: The modified FoodStockPile
        """
        food = Food(food_name)
        if food.is_rare_food_item():
            raise FoodException(msg=f"Not Supported: {food_name=} is not supported.",
                                food=food)

        cur_quantity = self.__stockpile[food_name]

        if cur_quantity + n < 0:
            msg = (f"Insufficient food: Cannot remove {n=} of food from the stockpile\n"
                   f"The current quantity of {food_name} is {cur_quantity}.")
            raise FoodException(msg, food=Food(food_name))

        self.__stockpile[food_name] += n

        return self

    def add_food_dict(self, food_dict: Dict[str, int]) -> "FoodStockpile":
        """
        Add an entire food dict to the stockpile.

        Note that negative values will reduce the number of food items in this
        FoodStockPile

        :param food_dict:
        :return: the modified FoodStockPile
        """
        for food_name, times in food_dict.items():
            self.add_food(food_name, n=times)

        return self

    def get_most_abundant_food(self) -> str:
        """
        Return the most abundant food in the stockpile. If multiple food items
        occur equally most frequent, return one of them. This function makes
        no guarantee which is returned in that case.
        """
        return max(self.__stockpile, key=self.__stockpile.get)

    def has_sufficient(self, food_name: str, *, n: int) -> bool:
        """Return True if the stockpile has >=n of the specified food item."""
        return self.__stockpile[food_name] >= n

    def has_sufficient_abundant_food(self, *, n: int):
        """Return True if the stockpile has >=n of the most abundant food item."""
        food_name: str = self.get_most_abundant_food()
        return self.has_sufficient(food_name, n=n)

    def as_dict(self) -> Dict[str, int]:
        """Return a deep copy of the underlying data."""
        return copy.deepcopy(self.__stockpile)


class FoodStockpileBuilder:
    """
    Class that creates a FoodStockpile using the builder
    design pattern.
    """

    def __init__(self):
        self.__stockpile: Dict[str, int] = self.__empty_stockpile()

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.__stockpile})"

    def user(self, habitica_user: HabiticaUser) -> "FoodStockpileBuilder":
        """
        Add a user's food to the stockpile. This ignores saddles,
        cakes, and other rare foods.
        :param habitica_user:
        :return: self
        """
        food: Dict[str, int] = habitica_user.get_food()
        for food_name, quantity in food.items():
            if Food(food_name).is_rare_food_item() is False:
                self.__stockpile[food_name] = quantity
        return self

    def build(self) -> FoodStockpile:
        """
        Build a normalized FoodStockpile. This stockpile never has rare items, and
        it add a 0 count for foods that we don't have.
        """
        return FoodStockpile(self.__stockpile)

    @staticmethod
    def __empty_stockpile() -> Dict[str, int]:
        no_food = 0
        return dict.fromkeys(FoodData.drop_food_names, no_food)

    @classmethod
    def empty_stockpile(cls) -> FoodStockpile:
        """Create an empty stockpile."""
        return FoodStockpile(FoodStockpileBuilder.__empty_stockpile())
