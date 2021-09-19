from typing import Dict

import pytest

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.zoo.foodmodels import Food, FeedingStatus, \
    FoodException, FoodStockpile, FoodStockpileBuilder


class TestFeedingStatus:
    @pytest.mark.parametrize(
        "feeding_status,expected_percentage",
        [(-1, 100), (5, 10), (7, 14), (48, 96)]
    )
    def test_to_percentage_ok(self, feeding_status: int,
                              expected_percentage: int):
        feeding_status = FeedingStatus(feeding_status)

        result_percentage = feeding_status.to_percentage()

        assert result_percentage == expected_percentage

    @pytest.mark.parametrize(
        "start_status,expected_food_items", [
            (45, 1),
            (44, 2),
            (40, 2),
            (39, 3),
            (5, 9),
        ]
    )
    def test_required_food_items_to_become_mount_favorite(self,
                                                          start_status: int,
                                                          expected_food_items: int):
        feeding_status = FeedingStatus(start_status)

        is_favorite = True
        result = feeding_status.required_food_items_to_become_mount(is_favorite)

        assert result == expected_food_items

    @pytest.mark.parametrize(
        "start_status,expected_food_items", [
            (49, 1),
            (45, 3),
            (44, 3),
            (40, 5),
            (39, 6),
            (6, 22),
            (5, 23),
        ]
    )
    def test_required_food_items_to_become_mount_not_favorite(self,
                                                              start_status: int,
                                                              expected_food_items: int):
        feeding_status = FeedingStatus(start_status)

        is_favorite = False
        result = feeding_status.required_food_items_to_become_mount(is_favorite)

        assert result == expected_food_items


class TestFeedingStatusHash:
    _feeding_statuses = [
        FeedingStatus(-1), FeedingStatus(), FeedingStatus(5),
        FeedingStatus(20), FeedingStatus(35), FeedingStatus(49)
    ]

    @pytest.mark.parametrize(
        "feeding_status", _feeding_statuses
    )
    def test___hash__(self, feeding_status: FeedingStatus):
        # A minimal requirement for __hash__ is that if 2 FeedingStatus objects are
        # identical, they MUST have the same hash.
        assert hash(feeding_status) == hash(feeding_status)

    @pytest.mark.parametrize(
        "feeding_status,equal_feeding_status",
        list(zip(_feeding_statuses + [FeedingStatus()],
                 _feeding_statuses + [FeedingStatus(5)]))
    )
    def test___hash__(self,
                      feeding_status: FeedingStatus,
                      equal_feeding_status: FeedingStatus):
        # A minimal requirement for __hash__ if 2 FeedingStatus objects
        # are equal (__eq__) , they MUST have the same hash.
        assert hash(feeding_status) == hash(feeding_status)


class TestFood:

    @pytest.mark.parametrize("food_name", [
        "RottenMeat", "CottonCandyBlue", "Chocolate", "Fish",
        "Saddle", "Cake_Skeleton", "Pie_White", "Candy_Zombie"
    ])
    def test___repr__(self, food_name: str):
        food = Food(food_name)
        result = str(food)

        assert result == f"Food({food_name})"

    @pytest.mark.parametrize("food_name,is_rare_expected", [
        ("RottenMeat", False),
        ("CottonCandyPink", False),
        ("Saddle", True),
        ("Cake_Skeleton", True),
        ("Pie_White", True),
        ("Candy_Zombie", True)
    ])
    def test_is_rare(self, food_name: str, is_rare_expected):
        food = Food(food_name)

        result_is_rare: bool = food.is_rare_food_item()

        assert result_is_rare == is_rare_expected


def get_empty_stockpile_dict() -> Dict[str, int]:
    return {'Meat': 0, 'Milk': 0, 'Potatoe': 0, 'Strawberry': 0,
            'Chocolate': 0, 'Fish': 0, 'RottenMeat': 0,
            'CottonCandyPink': 0, 'CottonCandyBlue': 0, 'Honey': 0}


class TestFoodStockpileBuilder:

    def test_build_empty(self):
        result_stockpile: FoodStockpile = FoodStockpileBuilder().build()

        expected_stockpile = get_empty_stockpile_dict()
        assert result_stockpile.as_dict() == expected_stockpile

    def test_build(self):
        drop_food = {"RottenMeat": 201, "CottonCandyBlue": 71, "Chocolate": 1}
        food_dict = {"items": {"food": {
            **drop_food, "Saddle": 1, "Cake_Skeleton": 1, "Pie_White": 2, "Candy_Zombie": 1}
        }}
        user = HabiticaUser(user_dict=food_dict)

        result_stockpile = FoodStockpileBuilder().user(user).build()

        expected_food = get_empty_stockpile_dict()
        expected_food.update(drop_food)

        assert result_stockpile.as_dict() == expected_food

    def test___repr__(self):
        drop_food = {"RottenMeat": 201}
        food_dict = {"items": {"food": {**drop_food, "Saddle": 11}}}
        user = HabiticaUser(user_dict=food_dict)

        stockpile = FoodStockpileBuilder().user(user)
        result = str(stockpile)

        expected_food = get_empty_stockpile_dict()
        expected_food.update(drop_food)
        expected_repr = f"FoodStockpileBuilder({expected_food})"
        assert result == expected_repr

    def test_empty_stockpile(self):
        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        assert all(amount == 0 for amount in stockpile.as_dict().values())


class TestFoodStockpile:
    def get_user_with_empty_stockpile(self) -> HabiticaUser:
        empty_stockpile: Dict[str, int] = get_empty_stockpile_dict()
        return HabiticaUser({"items": {"food": empty_stockpile}})

    def test_add_food_ok(self):
        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        food1, amount1 = "Meat", 5
        food2, amount2 = "Honey", 1
        stockpile.add_food(food1, n=amount1)
        stockpile.add_food(food2, n=amount2)

        expected_food = get_empty_stockpile_dict()
        expected_food.update({food1: amount1, food2: amount2})
        assert stockpile.as_dict() == expected_food
        assert str(stockpile) == f"FoodStockpile({expected_food})"

    def test_add_food_supply_too_small_fail(self):
        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        food_name = "CottonCandyBlue"
        with pytest.raises(FoodException) as execinfo:
            # can't subtract anything anything from empty stockpile
            stockpile.add_food(food_name, n=-1)

        msg = str(execinfo.value)
        expected_msg = (f"Insufficient food: Cannot remove n=-1 of food from the stockpile\n"
                        f"The current quantity of {food_name} is 0.")

        expected_food = Food(food_name)

        assert msg == expected_msg
        assert execinfo.value.food == expected_food

    def test_add_rare_food_item_fail(self):
        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        food_name = "Saddle"
        with pytest.raises(FoodException) as execinfo:
            # Saddles are not supported by our stockpile
            stockpile.add_food(food_name, n=1)

        msg = str(execinfo.value)
        expected_msg = f"Not Supported: {food_name=} is not supported."
        expected_food = Food(food_name)

        assert msg == expected_msg
        assert execinfo.value.food == expected_food

    def test_add_food_dict(self):
        food_dict = {"Meat": 9, "CottonCandyBlue": 8, "Honey": 7}
        food_dict2 = {"Meat": -3, "Fish": 1}

        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        stockpile.add_food_dict(food_dict)
        stockpile.add_food_dict(food_dict2)

        expected_stockpile = FoodStockpile(
            {'Chocolate': 0, 'CottonCandyBlue': 8, 'CottonCandyPink': 0, 'Fish': 1, 'Honey': 7,
             'Meat': 6, 'Milk': 0, 'Potatoe': 0, 'RottenMeat': 0, 'Strawberry': 0})
        assert stockpile == expected_stockpile

    def test_get_most_abundant_food(self):
        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        most_abundant_food, most_abundant_frequency = "Strawberry", 10
        stockpile.add_food(most_abundant_food, n=most_abundant_frequency)
        stockpile.add_food("Meat", n=most_abundant_frequency - 2)
        stockpile.add_food("CottonCandyBlue", n=most_abundant_frequency - 5)

        result_food: str = stockpile.get_most_abundant_food()

        assert result_food == most_abundant_food

    @pytest.mark.parametrize(
        "food_name,n", [("Meat", 0), ("Milk", 8), ("Honey", 10), ("Strawberry", 11)]
    )
    def test_has_sufficient(self, food_name: str, n: int):
        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        start_quantity = 10
        stockpile.add_food(food_name, n=start_quantity)

        result_sufficient: bool = stockpile.has_sufficient(food_name, n=n)

        # If the start quantity is larger than the required n items, then you have
        #  sufficient number of this food item.
        expected_sufficient = start_quantity >= n
        assert result_sufficient == expected_sufficient

    def test_has_sufficient_abundant_food(self):
        stockpile: FoodStockpile = FoodStockpileBuilder.empty_stockpile()

        abundant_food, abundant_food_quantity = "Meat", 12
        other_food = "Strawberry"
        stockpile.add_food(abundant_food, n=abundant_food_quantity)
        stockpile.add_food(other_food, n=abundant_food_quantity - 10)

        assert stockpile.has_sufficient_abundant_food(n=0)
        assert stockpile.has_sufficient_abundant_food(n=abundant_food_quantity - 1)
        assert stockpile.has_sufficient_abundant_food(n=abundant_food_quantity)
        assert stockpile.has_sufficient_abundant_food(n=abundant_food_quantity + 1) is False
