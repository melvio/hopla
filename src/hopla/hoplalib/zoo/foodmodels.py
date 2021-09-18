"""
A helper module for feeding logic.
"""
import math
from dataclasses import dataclass
from typing import Dict, Optional

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.clickhelper import PrintableException


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


class FoodData:
    """
    Helper class with valid Habitica _stockpile and drop hatching potions and
    the relationship between them.
    """

    hatching_potion_favorite_food_mapping = {
        "Base": "Meat",
        "White": "Milk",
        "Desert": "Potatoe",
        "Red": "Strawberry",
        "Shade": "Chocolate",
        "Skeleton": "Fish",
        "Zombie": "RottenMeat",
        "CottonCandyPink": "CottonCandyPink",
        "CottonCandyBlue": "CottonCandyBlue",
        "Golden": "Honey"
    }
    """
    Note: Pets hatched with magic hatching potions prefer any type of _stockpile.
    These pets are not supported by this dict.
    Rare favorite foods are also not supported such as Cake, Candy, and Pie.

    @see:
    * <https://habitica.fandom.com/wiki/Food_Preferences>
    * hopla api content | jq .dropHatchingPotions
    * hopla api content | jq .dropEggs

    also interesting:
    * hopla api content | jq .questEggs
    * hopla api content | jq .hatchingPotions
    * hopla api content | jq .premiumHatchingPotions
    * hopla api content | jq. wackyHatchingPotions
    """

    drop_hatching_potions = list(hatching_potion_favorite_food_mapping.keys())
    """A list of the non magic, non special hatching potions"""

    drop_food_names = list(hatching_potion_favorite_food_mapping.values())
    """A list of _stockpile that can be dropped by doing tasks.

    These dont include cakes etc., those are rare collectibles.

    # for more info @see:
    #    hopla api content | jq .food
    #    hopla api content | jq '.food[] | select(.canDrop==true)'
    #    hopla api content | jq '[.food[] | select(.canDrop==true) | .key]'
    """


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
        Return False if the _stockpile item is a drop _stockpile.
        Else return True.
        """
        return self.food_name not in FoodData.drop_food_names


class FoodStockpile:
    """The food of a user."""

    def __init__(self, _stockpile: Dict[str, int]):
        self.__stockpile = _stockpile

    def __repr__(self):
        return self.__class__.__name__ + f"({self.__dict__})"

    def modify_stockpile(self, food_name: str, *, amount: int) -> None:
        """
        Change the number of specified food in the stockpile.

        :param food_name: the food to modify
        :param amount: when positive add this number of food, when negative subtract
                it from the stockpile
        :return:
        """
        food = Food(food_name)
        if food.is_rare_food_item():
            raise FoodException(msg=f"Not Supported: {food_name=} is not supported.",
                                food=food)

        cur_quantity = self.__stockpile[food_name]

        if cur_quantity + amount < 0:
            msg = (f"Insufficient food: Cannot remove {amount=} of food from the stockpile\n"
                   f"The current quantity of {food_name=} is {cur_quantity=}.")
            raise FoodException(msg, food=Food(food_name))

        self.__stockpile[food_name] += amount

    def get_most_abundant_food(self) -> str:
        """Return the most abundant food in the stockpile."""
        return max(self.__stockpile, key=self.__stockpile.get)

    def has_eq_or_more_of_food(self, food_name: str, *, n: int) -> bool:
        """Return True if the stockpile has >=n of the specified food item."""
        return self.__stockpile[food_name] >= n

    def has_eq_or_more_of_most_abundant_food(self, *, n: int):
        """Return True if the stockpile has >=n of the most abundant food item."""
        food_name: str = self.get_most_abundant_food()
        return self.has_eq_or_more_of_food(food_name, n=n)


class FoodStockpileBuilder:
    """
    Class that creates a FoodStockpile using the builder
    design pattern.
    """

    def __init__(self):
        self.__stockpile: Dict[str, int] = self.__empty_stockpile()

    def __repr__(self):
        return self.__class__.__name__ + f"({self.__dict__})"

    def user(self, habitica_user: HabiticaUser):
        """
        Add a user's _stockpile to the stockpile. This ignores saddles,
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
