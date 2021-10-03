#!/usr/bin/env python3
from typing import List

import pytest

from hopla.hoplalib.hatchery.eggmodels import Egg, EggCollection
from hopla.hoplalib.hatchery.hatchalgorithms import HatchPlan, HatchPlanItem, HatchPlanMaker
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchPotion, HatchPotionCollection
from hopla.hoplalib.zoo.foodmodels import FeedStatus
from hopla.hoplalib.zoo.petmodels import Pet


class TestHatchPlanItem:
    def test__repr__ok(self):
        egg_name, potion_name = "Wolf", "Aquatic"
        egg = Egg(egg_name, quantity=2)
        potion = HatchPotion(potion_name, quantity=3)
        plan_item = HatchPlanItem(egg=egg, potion=potion)

        result: str = repr(plan_item)

        assert result == f"HatchPlanItem({egg_name}: {potion_name})"

    def test__eq__should_eq_self_ok(self):
        egg_name, potion_name = "Snake", "Base"
        egg = Egg(egg_name)
        potion = HatchPotion(potion_name)
        item = HatchPlanItem(egg=egg, potion=potion)

        assert item == item

    def test__eq__should_ignore_quantity_differences_true(self):
        egg_name, potion_name = "Snake", "Base"

        item_self = HatchPlanItem(
            egg=Egg(egg_name, quantity=2),
            potion=HatchPotion(potion_name, quantity=3)
        )

        item_other = HatchPlanItem(
            egg=Egg(egg_name, quantity=12),
            potion=HatchPotion(potion_name, quantity=103)
        )

        assert item_self == item_other

    def test__eq__different_egg_name_false(self):
        potion_name = "Base"
        item_self = HatchPlanItem(egg=Egg("Snake"), potion=HatchPotion(potion_name))
        item_other = HatchPlanItem(egg=Egg("Horse"), potion=HatchPotion(potion_name))

        assert item_self != item_other

    def test__eq__different_potion_name_false(self):
        egg_name = "Horse"
        item_self = HatchPlanItem(egg=Egg(egg_name), potion=HatchPotion("Base"))
        item_other = HatchPlanItem(egg=Egg(egg_name), potion=HatchPotion("CottonCandyBlue"))

        assert item_self != item_other

    def test__eq__different_thing_false(self):
        item_self = HatchPlanItem(egg=Egg("Horse"), potion=HatchPotion("Base"))

        assert item_self != Egg("Snake")
        assert item_self != HatchPotion("Base")

    def test_format_item(self):
        egg_name = "Snake"
        potion_name = "Base"
        item = HatchPlanItem(egg=Egg(egg_name), potion=HatchPotion(potion_name))

        result: str = item.format_item()

        expected = f"A {egg_name} egg will be hatched by a {potion_name} potion.\n"
        assert result == expected


class TestHatchPlan:
    def test__init__(self):
        hatch_plan = HatchPlan()
        assert hatch_plan.plan == []

    def test__repr__empty(self):
        hatch_plan = HatchPlan()

        result: str = repr(hatch_plan)

        assert result == "HatchPlan(empty)"

    def test__repr__not_empty(self):
        hatch_plan = HatchPlan()
        egg_name = "Horse"
        potion_name = "CottonCandyBlue"
        hatch_plan.add(egg=Egg(egg_name), potion=HatchPotion(potion_name))

        result: str = repr(hatch_plan)

        assert result == f"HatchPlan([HatchPlanItem({egg_name}: {potion_name})])"

    def test_format_plan(self):
        plan = HatchPlan() \
            .add(egg=Egg("Fox"), potion=HatchPotion("Dessert")) \
            .add(egg=Egg("Seahorse"), potion=HatchPotion("Desert"))

        result: str = plan.format_plan()

        expected: str = (
            "A Fox egg will be hatched by a Dessert potion.\n"
            "A Seahorse egg will be hatched by a Desert potion.\n"
        )

        assert result == expected

    def test_is_empty_true(self):
        plan = HatchPlan()
        assert plan.is_empty() is True
        assert len(plan) == 0

    def test_is_empty_false(self):
        plan = HatchPlan().add(egg=Egg("Egg"), potion=HatchPotion("Red"))
        assert plan.is_empty() is False
        assert len(plan) == 1

    def test_add_ok(self):
        hatch_plan = HatchPlan()
        egg = Egg("Seahorse")
        potion = HatchPotion("Skeleton")
        hatch_plan.add(egg=egg, potion=potion)

        assert len(hatch_plan) == 1
        assert HatchPlanItem(egg, potion) in hatch_plan

    def test_remove_hatch_item_if_pet_available_empty_ok(self):
        empty: List[Pet] = []
        egg = Egg("Wolf")
        potion = HatchPotion("Ghost")
        hatch_plan = HatchPlan().add(egg=egg, potion=potion)

        hatch_plan.remove_hatch_item_if_pet_available(empty)

        assert len(hatch_plan) == 1
        assert HatchPlanItem(egg, potion) in hatch_plan

    def test_remove_hatch_item_if_pet_available_yes_available_ok(self):
        pets: List[Pet] = [Pet("Wolf-Ghost", feed_status=FeedStatus(5))]
        egg = Egg("Wolf")
        potion = HatchPotion("Ghost")
        hatch_plan = HatchPlan().add(egg=egg, potion=potion)

        hatch_plan.remove_hatch_item_if_pet_available(pets)

        assert len(hatch_plan) == 0
        assert HatchPlanItem(egg, potion) not in hatch_plan

    def test_remove_hatch_item_if_pet_available_yes_and_no_available_ok(self):
        # 1. Wolf-Ghost is available, so that one should be filtered out.
        # 2. However, even though Wolf-Base is in the list, it is not available because
        #    feed status is -1.
        pets: List[Pet] = [
            Pet("Wolf-Ghost", feed_status=FeedStatus(5)),
            Pet("Wolf-Base", feed_status=FeedStatus(-1))
        ]
        egg = Egg("Wolf")
        ghost_potion = HatchPotion("Ghost")
        base_potion = HatchPotion("Base")
        hatch_plan = HatchPlan() \
            .add(egg=egg, potion=ghost_potion) \
            .add(egg=egg, potion=base_potion)

        hatch_plan.remove_hatch_item_if_pet_available(pets)

        assert len(hatch_plan) == 1
        assert HatchPlanItem(egg, base_potion) in hatch_plan
        assert HatchPlanItem(egg, ghost_potion) not in hatch_plan

    def test__iter__(self):
        egg1, egg2 = Egg("Wolf"), Egg("Egg")
        ghost_potion = HatchPotion("Ghost")
        base_potion = HatchPotion("Base")
        hatch_plan = HatchPlan() \
            .add(egg=egg1, potion=ghost_potion) \
            .add(egg=egg2, potion=base_potion)

        iter_result = iter(hatch_plan)
        assert next(iter_result) == HatchPlanItem(egg=egg1, potion=ghost_potion)
        assert next(iter_result) == HatchPlanItem(egg=egg2, potion=base_potion)
        with pytest.raises(StopIteration):
            next(iter_result)


class TestHatchPlanMaker:
    def test__repr__(self):
        eggs = EggCollection({"Wolf": 1, "Whale": 2})
        potions = HatchPotionCollection({"Base": 1, "Ember": 2})
        plan_maker = HatchPlanMaker(egg_collection=eggs, hatch_potion_collection=potions)

        result: str = repr(plan_maker)

        assert result == (
            f"HatchPlanMaker(\n"
            f"    {eggs},\n"
            f"    {potions},\n"
            f"    plan=HatchPlan(empty)\n"
            ")"
        )

    def test_make_plan_no_eggs(self):
        empty_eggs = EggCollection()
        potions = HatchPotionCollection({"Zombie": 1})

        plan_maker = HatchPlanMaker(egg_collection=empty_eggs, hatch_potion_collection=potions)

        result: HatchPlan = plan_maker.make_plan()

        expected_empty_plan = HatchPlan()
        assert result == expected_empty_plan

    def test_make_plan_no_hatch_potions(self):
        eggs = EggCollection({"Owl": 1})
        empty_potions = HatchPotionCollection()
        plan_maker = HatchPlanMaker(egg_collection=eggs, hatch_potion_collection=empty_potions)

        result: HatchPlan = plan_maker.make_plan()

        expected_empty_plan = HatchPlan()
        assert result == expected_empty_plan

    def test_make_plan_1potion_1egg_ok(self):
        eggs = EggCollection({"Owl": 1})
        potions = HatchPotionCollection({"Base": 1})
        plan_maker = HatchPlanMaker(egg_collection=eggs, hatch_potion_collection=potions)

        result: HatchPlan = plan_maker.make_plan()

        expected = HatchPlan().add(egg=Egg("Owl"), potion=HatchPotion("Base"))
        assert result == expected

    def test_make_plan_1magic_potion_1quest_egg_ok(self):
        eggs = EggCollection({"Owl": 1})
        magic_potions = HatchPotionCollection({"Thunderstorm": 1})
        plan_maker = HatchPlanMaker(egg_collection=eggs, hatch_potion_collection=magic_potions)

        result: HatchPlan = plan_maker.make_plan()

        expected_empty_plan = HatchPlan()
        assert result == expected_empty_plan

    def test_make_plan_1magic_potion_2normal_1quest_egg_ok(self):
        eggs = EggCollection({"Owl": 1, "Fox": 2})
        magic_potions = HatchPotionCollection({"Thunderstorm": 1})
        plan_maker = HatchPlanMaker(egg_collection=eggs, hatch_potion_collection=magic_potions)

        result: HatchPlan = plan_maker.make_plan()

        expected = HatchPlan().add(egg=Egg("Fox"),
                                   potion=HatchPotion("Thunderstorm"))
        assert result == expected

    def test_make_plan_more_potions_than_eggs(self):
        eggs = EggCollection({"Horse": 1, "Cactus": 2})
        potions = HatchPotionCollection(
            {"SolarSystem": 2, "Zombie": 1, "Base": 1, "Fluorite": 1, "Shade": 3}
        )
        plan_maker = HatchPlanMaker(egg_collection=eggs, hatch_potion_collection=potions)

        result: HatchPlan = plan_maker.make_plan()

        expected = HatchPlan() \
            .add(egg=Egg("Horse"), potion=HatchPotion("Zombie")) \
            .add(egg=Egg("Cactus"), potion=HatchPotion("SolarSystem")) \
            .add(egg=Egg("Cactus"), potion=HatchPotion("Base")) \
            # ^ Can't hatch same Cactus twice with same potion

        assert result == expected
