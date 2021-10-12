"""
A modules with algorithms for feeding multiple pets at once.
"""
from dataclasses import dataclass
from typing import Iterator, List
from copy import deepcopy

from hopla.hoplalib.zoo.foodmodels import FoodStockpile
from hopla.hoplalib.zoo.petmodels import Pet
from hopla.hoplalib.zoo.zoomodels import Zoo, ZooHelper


@dataclass(frozen=True)
class FeedPlanItem:
    """An item of a feed plan.

    An item on the feed plan describes exactly what food to feed 1 single pet.
    """
    pet_name: str
    food_name: str
    times: int

    def format_item(self) -> str:
        """A to string function for nice terminal output"""
        return f"Pet {self.pet_name} will get {self.times} {self.food_name}."


@dataclass
class FeedPlan:
    """A plan to feed pets.

    This class acts as a wrapper around a list with feeding parameters.
    """

    def __init__(self):
        self.__feed_plan: [FeedPlanItem] = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(__feed_plan={self.__feed_plan})"

    def __iter__(self) -> Iterator[FeedPlanItem]:
        return iter(self.__feed_plan)

    def __len__(self) -> int:
        """Return the number of FeedPlanItems in this feed plan."""
        return len(self.__feed_plan)

    def isempty(self) -> bool:
        """Return true if the feed plan is empty."""
        return len(self) == 0

    def add_to_feed_plan(self, *, pet_name: str, food_name: str, times: int) -> None:
        """Add an item to the feed plan.

        :param pet_name: name of the pet to feed
        :param food_name: name of the food to give
        :param times: number of food items to give
        :return: None
        """
        feed_item = FeedPlanItem(
            pet_name=pet_name,
            food_name=food_name,
            times=times
        )
        self.__feed_plan.append(feed_item)

    @property
    def feed_plan(self) -> List[FeedPlanItem]:
        """Return the feed plan.

        :return: The feed plan. This will be empty when
        no feed plan items have been added yet.
        """
        return self.__feed_plan

    def format_plan(self) -> str:
        """A to string function for nice terminal output"""
        return "\n".join([item.format_item() for item in self.__feed_plan])


@dataclass
class FeedAlgorithm:
    """
    This class contains an algorithm that makes a plan to distribute food
    from a food stockpile over all pets.
    """

    def __init__(self, *, zoo: Zoo, stockpile: FoodStockpile):
        self.__zoo: Zoo = ZooHelper(deepcopy(zoo)).get_feedable_zoo()
        self.__stockpile = deepcopy(stockpile)

        self.__feed_plan = FeedPlan()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(\n"
            f"  __feed_plan={self.__feed_plan.format_plan()}\n"
            f")"
        )

    @property
    def stockpile(self) -> FoodStockpile:
        """Return the stockpile."""
        return self.__stockpile

    @property
    def feed_plan(self) -> FeedPlan:
        """Return the underlying feed plan.

        This plan will be empty before calling make_plan.
        """
        return self.__feed_plan

    def make_plan(self) -> FeedPlan:
        """Make the plan.

        This function removes food from the stockpile and adds feed items
        to the feed plan.
        """
        helper = ZooHelper(self.__zoo)
        gen1_zoo: Zoo = helper.filter_on_pet(Pet.is_generation1_pet)
        quest_zoo: Zoo = helper.filter_on_pet(Pet.is_quest_pet)
        magic_zoo: Zoo = helper.filter_on_pet(Pet.is_magic_hatch_pet)

        self.__make_plan(gen1_zoo)
        self.__make_plan(quest_zoo)
        self.__make_plan(magic_zoo)

        return self.__feed_plan

    def __make_plan(self, zoo: Zoo):
        """Make plan for the specified zoo.

        This function assumes that only feedable pets are passed.
        """
        for pet_name, pair in zoo.items():
            pet: Pet = pair.pet

            if pet.has_just_1_favorite_food():
                food_name: str = pet.favorite_food()
            else:
                food_name: str = self.__stockpile.get_most_abundant_food()

            times: int = pet.required_food_items_until_mount(food_name)
            if self.__stockpile.has_sufficient(food_name, n=times):
                subtract_times: int = -times
                self.__stockpile.add_food(food_name,
                                          n=subtract_times)
                self.__feed_plan.add_to_feed_plan(
                    pet_name=pet_name,
                    food_name=food_name,
                    times=times
                )
