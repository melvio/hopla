#!/usr/bin/env python3
import pytest

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.zoo.fooddata import FoodData
from hopla.hoplalib.zoo.foodmodels import FoodStockpile, FoodStockpileBuilder
from hopla.hoplalib.zoo.zoomodels import Zoo, ZooBuilder
from hopla.hoplalib.zoo.zoofeed_algorithms import FeedPlanItem, \
    FeedAlgorithm, FeedPlan
from tests.testutils.user_test_utils import UserTestUtil


def plan_with_single_item(food_name: str, pet_name: str, times: int) -> FeedPlan:
    plan = FeedPlan()
    plan.add_to_feed_plan(pet_name=pet_name, food_name=food_name, times=times)
    return plan


class TestFeedPlan:

    def test___init___ok(self):
        plan = FeedPlan()

        assert plan.feed_plan == []

    def test__repr__empty(self):
        plan = FeedPlan()
        result: str = repr(plan)
        assert result == "FeedPlan(__feed_plan=[])"

    def test__repr__nonempty(self):
        pet_name = "Wolf-White"
        food_name = "Milk"
        times = 2
        plan: FeedPlan = plan_with_single_item(food_name, pet_name, times)

        result: str = repr(plan)

        assert f"{pet_name=}" in result
        assert f"{food_name=}" in result
        assert f"{times=}" in result

    @pytest.mark.parametrize("plan,expected_empty", [
        (plan_with_single_item("Wolf-Red", "Fish", 1), False),
        (FeedPlan(), True)
    ])
    def test__is_empty(self, plan: FeedPlan, expected_empty: bool):
        assert plan.isempty() is expected_empty

    @pytest.mark.parametrize("plan,expected_len", [
        (plan_with_single_item("Wolf-Red", "Strawberry", 3), 1),
        (FeedPlan(), 0)
    ])
    def test__len(self, plan: FeedPlan, expected_len: int):
        assert len(plan) == expected_len

    def test_format_plan_empty(self):
        result: str = FeedPlan().format_plan()
        assert result == ""

    def test_format_plan_non_empty(self):
        pet_name = "Rat-Shade"
        food_name = "Chocolate"
        times = 8
        plan: FeedPlan = plan_with_single_item(
            pet_name=pet_name, food_name=food_name, times=times
        )

        result: str = plan.format_plan()
        assert result == f'Pet {pet_name} will get {times} {food_name}.'

    def test_add_to_feed_plan_ok(self):
        plan = FeedPlan()
        pet_name = "Axolotl-Zombie"
        food_name = "RottenMeat"
        times = 9
        plan.add_to_feed_plan(pet_name=pet_name,
                              food_name=food_name,
                              times=times)

        expected_plan = [
            FeedPlanItem(pet_name=pet_name, food_name=food_name, times=times)
        ]
        assert plan.feed_plan == expected_plan


class TestFeedAlgorithm:

    def test__repr__(self, feedable_pets_zoo: Zoo,
                     filled_stockpile: FoodStockpile):
        algorithm = FeedAlgorithm(zoo=feedable_pets_zoo, stockpile=filled_stockpile)

        repr_before: str = repr(algorithm)
        plan: FeedPlan = algorithm.make_plan()
        repr_after: str = repr(algorithm)

        before_expected = "FeedAlgorithm(\n  __feed_plan=\n)"
        assert repr_before == before_expected

        after_expected = f"FeedAlgorithm(\n  __feed_plan={plan.format_plan()}\n)"
        assert repr_after == after_expected

    def test_make_plan_empty_stockpile_results_in_empty_plan_ok(self,
                                                                empty_zoo,
                                                                empty_stockpile):
        algorithm = FeedAlgorithm(zoo=empty_zoo,
                                  stockpile=empty_stockpile)

        plan: FeedPlan = algorithm.make_plan()

        expected_empty_plan = FeedPlan()
        assert plan == expected_empty_plan
        assert algorithm.stockpile == empty_stockpile

    def test_make_plan_empty_stockpile_filled_zoo_results_in_empty_plan_ok(self,
                                                                           feedable_pets_zoo,
                                                                           empty_stockpile):
        algorithm = FeedAlgorithm(zoo=feedable_pets_zoo,
                                  stockpile=empty_stockpile)

        plan: FeedPlan = algorithm.make_plan()

        expected_empty_plan = FeedPlan()
        assert plan == expected_empty_plan
        assert algorithm.stockpile == empty_stockpile

    def test_make_plan_filled_stockpile_empty_zoo_results_in_empty_plan_ok(self,
                                                                           empty_zoo,
                                                                           filled_stockpile):
        algorithm = FeedAlgorithm(zoo=empty_zoo,
                                  stockpile=filled_stockpile)

        plan: FeedPlan = algorithm.make_plan()

        expected_empty_plan = FeedPlan()
        assert plan == expected_empty_plan

    def test_make_plan_filled_stockpile_hungry_zoo_results_in_plan_ok(self):
        # Wolf-Shade can be fed 9 times
        pet1, food1, food1_amount = "Wolf-Shade", "Chocolate", 10
        # Alligator-Golden can be fed 8 times
        pet2, food2, food2_amount = "Alligator-Golden", "Honey", 10
        # Wolf-Red can be fed 5 times
        pet3, food3, food3_amount = "Wolf-Red", "Strawberry", 10
        # TigerCub-Fluorite takes whatever food is most abundant
        pet4, food4, food4_amount = "TigerCub-Fluorite", "Fish", 20  # most abundant
        unused_food, unused_food_amount = "CottonCandyBlue", 5

        hungry_pets = {pet1: 5, pet2: 10, pet3: 25, pet4: 49}
        zoo: Zoo = ZooBuilder(UserTestUtil.user_with_zoo(pets=hungry_pets)).build()

        start_stockpile = (
            FoodStockpileBuilder.empty_stockpile().add_food_dict({
                food1: food1_amount, food2: food2_amount, food3: food3_amount,
                food4: food4_amount, unused_food: unused_food_amount,
            })
        )

        algorithm = FeedAlgorithm(zoo=zoo, stockpile=start_stockpile)

        result_plan: FeedPlan = algorithm.make_plan()

        expected_first_pet_feed_times = 9
        expected_second_pet_feed_times = 8
        expected_third_pet_feed_times = 5
        expected_fourth_pet_feed_times = 1
        expected_stockpile = (
            FoodStockpileBuilder.empty_stockpile().add_food_dict({
                food1: food1_amount - expected_first_pet_feed_times,
                food2: food2_amount - expected_second_pet_feed_times,
                food3: food3_amount - expected_third_pet_feed_times,
                unused_food: unused_food_amount,
                food4: food4_amount - expected_fourth_pet_feed_times
            })
        )
        expected_feed_plan = [
            FeedPlanItem(pet1, food1, expected_first_pet_feed_times),
            FeedPlanItem(pet2, food2, expected_second_pet_feed_times),
            FeedPlanItem(pet3, food3, expected_third_pet_feed_times),
            FeedPlanItem(pet4, food4, expected_fourth_pet_feed_times)
        ]

        assert algorithm.stockpile == expected_stockpile
        assert all(feed_item in result_plan for feed_item in expected_feed_plan)
        assert result_plan == algorithm.feed_plan  # sanity check

    def test_make_plan_feed_single_pet(self):
        pet_name = "Velociraptor-Skeleton"
        start_fish = 20
        food_name = "Fish"
        user = HabiticaUser({"items": {
            "pets": {pet_name: 10},
            "mounts": {},
            "food": {food_name: start_fish}
        }})
        zoo: Zoo = ZooBuilder(user).build()
        stockpile: FoodStockpile = FoodStockpileBuilder().user(user).build()
        algorithm = FeedAlgorithm(zoo=zoo, stockpile=stockpile)

        feed_plan: FeedPlan = algorithm.make_plan()

        expected_fish_given = 8
        assert len(feed_plan) == 1
        assert feed_plan.feed_plan[0] == FeedPlanItem(
            pet_name=pet_name,
            food_name=food_name,
            times=expected_fish_given
        )

        expected_fish_leftover: int = start_fish - expected_fish_given
        actual_fish_leftover = algorithm.stockpile.as_dict()[food_name]
        assert actual_fish_leftover == expected_fish_leftover

    @pytest.fixture
    def empty_stockpile(self) -> FoodStockpile:
        return FoodStockpileBuilder().build()

    @pytest.fixture
    def empty_zoo(self) -> Zoo:
        empty_zoo_user: HabiticaUser = UserTestUtil.user_with_zoo(pets=None, mounts=None)
        return ZooBuilder(empty_zoo_user).build()

    @pytest.fixture
    def feedable_pets_zoo(self) -> Zoo:
        hungry_pets = {"Parrot-Shade": 5, "Alligator-Golden": 10,
                       "Dragon-CottonCandyBlue": 20, "Wolf-Red": 25}
        user_with_feedable_pets: HabiticaUser = UserTestUtil.user_with_zoo(pets=hungry_pets)
        return ZooBuilder(user_with_feedable_pets).build()

    @pytest.fixture
    def filled_stockpile(self) -> FoodStockpile:
        stockpile = FoodStockpileBuilder().build()
        for food_name in FoodData.drop_food_names:
            lots_of_food = 100
            stockpile.add_food(food_name, n=lots_of_food)
        return stockpile
