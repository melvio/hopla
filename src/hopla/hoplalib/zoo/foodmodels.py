"""
A helper module for feeding logic.
"""
import copy
import math
from dataclasses import dataclass
from typing import Dict, Optional

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.clickhelper import PrintableException
from hopla.hoplalib.zoo.fooddata import FoodData


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
        # The feeding status of 0 is documented but never returned anno Sept 2021 to
        #  my understanding and according to a comment made by @Alys on github
        #  in 2020.
        invalid_status = (feeding_status < -1
                          or feeding_status in [0, 1, 2, 3, 4]
                          or feeding_status >= 50)
        if invalid_status:
            raise InvalidFeedingStatus(f"{feeding_status=} is invalid")

        self.__feeding_status = feeding_status

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.__feeding_status})"

    def __eq__(self, other):
        return isinstance(other, FeedingStatus) and int(other) == int(self)

    def __hash__(self):
        return hash(self.__feeding_status)

    def __int__(self) -> int:
        return self.__feeding_status

    def required_food_items_to_become_mount(self, is_favorite_food: bool) -> int:
        """Return how many items of food we need to give to turn a pet into a mount."""
        target = FeedingStatus.FULLY_FED_STATE - self.__feeding_status
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
        if self.__feeding_status == -1:
            return 100  # The pet is now a mount
        return self.__feeding_status * 2


class FoodException(PrintableException):
    """Exception thrown when there is a food error."""

    def __init__(self, msg: str, *, food: Optional["Food"] = None):
        super().__init__(msg)
        self.food = food


@dataclass(frozen=True)
class Food:
    """A stockpile food item."""
    food_name: str

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.food_name})"

    def is_rare_food_item(self) -> bool:
        """
        Return False if the food_item item is a drop food.
        Otherwise, return True.
        """
        return self.food_name not in FoodData.drop_food_names


class FoodStockpile:
    """The food of a user."""

    def __init__(self, __stockpile: Dict[str, int]):
        self.__stockpile = __stockpile

    def __repr__(self):
        return self.__class__.__name__ + f"({self.__stockpile})"

    def modify_stockpile(self, food_name: str, *, n: int) -> None:
        """
        Change the number of specified food in the stockpile.

        :param food_name: the food to modify
        :param n: When n is positive, add this number of food.
                  When negative, subtract n from this food from the stockpile.
        :return: None
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

    def __repr__(self):
        return self.__class__.__name__ + f"({self.__stockpile})"

    def user(self, habitica_user: HabiticaUser):
        """
        Add a user's food to the stockpile. This ignores saddles,
        cakes, and other rare foods.
        :param habitica_user:
        :return: self
        """
        food: Dict[str, int] = habitica_user.get_food()
        for food_name in food:
            quantity = food[food_name]
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