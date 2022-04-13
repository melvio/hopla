#!/usr/bin/env python3
from typing import List

import pytest

from hopla.hoplalib.hatchery.eggmodels import Egg, EggCollection
from hopla.hoplalib.hatchery.hatchalgorithms import HatchPlan, HatchPlanItem, HatchPlanMaker
from hopla.hoplalib.hatchery.egg_data import EggData
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

    @pytest.mark.parametrize("egg,potion", [
        (Egg("Wolf"), HatchPotion("Silver")),
        (Egg("Fox"), HatchPotion("Moonglow")),
        (Egg("Cactus"), HatchPotion("Watery")),
        (Egg("LionCub"), HatchPotion("Shade")),
        (Egg("PandaCub"), HatchPotion("Ruby")),
        (Egg("Whale"), HatchPotion("Base")),
        (Egg("Horse"), HatchPotion("Golden")),
        (Egg("Fox"), HatchPotion("Red"))
    ])
    def test__post_init_ok(self, egg: Egg, potion: HatchPotion):
        try:
            HatchPlanItem(egg=egg, potion=potion)
        except Exception:
            pytest.fail(f"Expected {egg.name} and {potion.name} to match.")

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

    @pytest.mark.parametrize("no_clash_pets", [
        Pet("Wolf-Bronze"),
        Pet("Fox-Base"),
        Pet("Wolf-Base", feed_status=FeedStatus(-1)),
        Pet("Wolf-Base", feed_status=FeedStatus(0))
    ])
    def test_can_hatch_with_pet_true(self, no_clash_pets: Pet):
        hatch_item = HatchPlanItem(egg=Egg("Wolf"), potion=HatchPotion("Base"))

        result = hatch_item.can_hatch_with_pet(no_clash_pets)

        assert result is True

    def test_can_hatch_with_pet_false(self):
        clash_pet = Pet("Wolf-Bronze")
        hatch_item = HatchPlanItem(egg=Egg("Wolf"), potion=HatchPotion("Bronze"))

        result = hatch_item.can_hatch_with_pet(clash_pet)

        assert result is False

    @pytest.mark.parametrize("hatch_item", [
        HatchPlanItem(Egg("Wolf"), HatchPotion("Bronze")),
        HatchPlanItem(Egg("Cactus"), HatchPotion("Amber")),
        HatchPlanItem(Egg("Horse"), HatchPotion("Shade"))
    ])
    def test_can_hatch_with_pets_no_pets_always_true(self, hatch_item: HatchPlanItem):
        result = hatch_item.can_hatch_with_pets([])
        assert result is True

    @pytest.mark.parametrize("hatch_item", [
        HatchPlanItem(Egg("Wolf"), HatchPotion("Bronze")),
        HatchPlanItem(Egg("Cactus"), HatchPotion("Amber")),
        HatchPlanItem(Egg("Horse"), HatchPotion("Shade")),
        HatchPlanItem(Egg("Wolf"), HatchPotion("Base")),
    ])
    def test_can_hatch_with_pets_no_clash_true(self, hatch_item: HatchPlanItem):
        no_clash_pets: List[Pet] = [
            Pet("Wolf-Base", feed_status=FeedStatus(0)),
            Pet("Cactus-Shade"),
            Pet("Seahorse-White"),
            Pet("Horse-Shade", feed_status=FeedStatus(-1))
        ]
        result = hatch_item.can_hatch_with_pets(no_clash_pets)
        assert result is True

    @pytest.mark.parametrize("hatch_item", [
        HatchPlanItem(Egg("Wolf"), HatchPotion("Bronze")),
        HatchPlanItem(Egg("Cactus"), HatchPotion("Amber")),
        HatchPlanItem(Egg("Horse"), HatchPotion("Shade")),
        HatchPlanItem(Egg("Wolf"), HatchPotion("Base")),
    ])
    def test_can_hatch_with_pets_clash_false(self, hatch_item: HatchPlanItem):
        clash_pets: List[Pet] = [
            Pet("Wolf-Bronze"), Pet("Cactus-Amber"), Pet("Horse-Shade"), Pet("Wolf-Base")
        ]
        result = hatch_item.can_hatch_with_pets(clash_pets)
        assert result is False


class TestHatchPlan:
    def test__init__(self):
        hatch_plan = HatchPlan()
        assert hatch_plan.plan == []

    def test__eq__empty(self):
        assert HatchPlan() == HatchPlan()

    def test__eq__false(self):
        plan = HatchPlan().add(egg=Egg("Whale"), potion=HatchPotion("Golden"))
        assert plan != HatchPlan()

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
        plan_maker = HatchPlanMaker(egg_collection=eggs, hatch_potion_collection=potions, pets=[])

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

        plan_maker = HatchPlanMaker(
            egg_collection=empty_eggs,
            hatch_potion_collection=potions,
            pets=[]
        )

        result: HatchPlan = plan_maker.make_plan()

        expected_empty_plan = HatchPlan()
        assert result == expected_empty_plan

    def test_make_plan_no_hatch_potions(self):
        eggs = EggCollection({"Owl": 1})
        empty_potions = HatchPotionCollection()
        plan_maker = HatchPlanMaker(
            egg_collection=eggs,
            hatch_potion_collection=empty_potions,
            pets=[]
        )

        result: HatchPlan = plan_maker.make_plan()

        expected_empty_plan = HatchPlan()
        assert result == expected_empty_plan

    def test_make_plan_1potion_1egg_ok(self):
        eggs = EggCollection({"Owl": 1})
        potions = HatchPotionCollection({"Base": 1})
        plan_maker = HatchPlanMaker(
            egg_collection=eggs,
            hatch_potion_collection=potions,
            pets=[]
        )

        result: HatchPlan = plan_maker.make_plan()

        expected = HatchPlan().add(egg=Egg("Owl"), potion=HatchPotion("Base"))
        assert result == expected

    def test_make_plan_1magic_potion_1quest_egg_ok(self):
        eggs = EggCollection({"Owl": 1})
        magic_potions = HatchPotionCollection({"Thunderstorm": 1})
        plan_maker = HatchPlanMaker(
            egg_collection=eggs,
            hatch_potion_collection=magic_potions,
            pets=[]
        )

        result: HatchPlan = plan_maker.make_plan()

        expected_empty_plan = HatchPlan()
        assert result == expected_empty_plan

    def test_make_plan_1magic_potion_2normal_1quest_egg_ok(self):
        eggs = EggCollection({"Owl": 1, "Fox": 2})
        magic_potions = HatchPotionCollection({"Thunderstorm": 1})
        plan_maker = HatchPlanMaker(
            egg_collection=eggs,
            hatch_potion_collection=magic_potions,
            pets=[]
        )

        result: HatchPlan = plan_maker.make_plan()

        expected = HatchPlan().add(egg=Egg("Fox"),
                                   potion=HatchPotion("Thunderstorm"))
        assert result == expected

    def test_make_plan_more_potions_than_eggs(self):
        eggs = EggCollection({"Horse": 1, "Cactus": 2})
        potions = HatchPotionCollection(
            {"SolarSystem": 2, "Zombie": 1, "Base": 1, "Fluorite": 1, "Shade": 3}
        )
        plan_maker = HatchPlanMaker(
            egg_collection=eggs,
            hatch_potion_collection=potions,
            pets=[]
        )

        result: HatchPlan = plan_maker.make_plan()

        expected = HatchPlan() \
            .add(egg=Egg("Horse"), potion=HatchPotion("Zombie")) \
            .add(egg=Egg("Cactus"), potion=HatchPotion("SolarSystem")) \
            .add(egg=Egg("Cactus"), potion=HatchPotion("Base")) \
            # ^ Can't hatch same Cactus twice with same potion

        assert result == expected

    def test_make_plan_with_pets(self):
        eggs = EggCollection({"Horse": 1, "Cactus": 3})
        potions = HatchPotionCollection(
            {"SolarSystem": 2, "Zombie": 1, "Base": 1, "Fluorite": 1, "Shade": 3}
        )
        pets: List[Pet] = [
            # This pet blocks hatching another Cactus-SolarSystem
            Pet("Cactus-SolarSystem"),
            # No blocking by Horse-Zombie pet. -1 means pet is not available.
            Pet("Horse-Zombie", feed_status=FeedStatus(-1))
        ]
        plan_maker = HatchPlanMaker(
            egg_collection=eggs,
            hatch_potion_collection=potions,
            pets=pets
        )

        result: HatchPlan = plan_maker.make_plan()

        expected = HatchPlan() \
            .add(egg=Egg("Horse"), potion=HatchPotion("Zombie")) \
            .add(egg=Egg("Cactus"), potion=HatchPotion("Base")) \
            .add(egg=Egg("Cactus"), potion=HatchPotion("Fluorite")) \
            .add(egg=Egg("Cactus"), potion=HatchPotion("Shade"))

        assert result == expected

    def test_make_plan_with_lots_of_pets_and_few_potions_ok(self):
        # case emulating the bug from: https://github.com/melvio/hopla/issues/184
        # Here there are lots of pets, lots of eggs, and only 3 vampire potions.
        # There are also only 3 pets available for hatching with those vampire potions.

        # lots of Eggs
        eggs = EggCollection(eggs={egg_name: 20 for egg_name in EggData.egg_names})
        # 3 vampire potions
        potions = HatchPotionCollection(potions={"Vampire": 3})
        # lots of vampire pets, only 3 hatch-able
        hatchable1, hatchable2, hatchable3 = "FlyingPig", "LionCub", "PandaCub"
        pets: List[Pet] = [
            Pet("BearCub-Vampire", feed_status=FeedStatus(5)),
            Pet("Cactus-Vampire", feed_status=FeedStatus(5)),
            Pet("Dragon-Vampire", feed_status=FeedStatus(5)),
            Pet(hatchable1 + "-Vampire", feed_status=FeedStatus(-1)),
            Pet("Fox-Vampire", feed_status=FeedStatus(5)),
            Pet(hatchable2 + "-Vampire", feed_status=FeedStatus(-1)),
            Pet(hatchable3 + "-Vampire", feed_status=FeedStatus(-1)),
            Pet("TigerCub-Vampire", feed_status=FeedStatus(5)),
            Pet("Wolf-Vampire", feed_status=FeedStatus(5)),
        ]

        plan_maker = HatchPlanMaker(
            egg_collection=eggs,
            hatch_potion_collection=potions,
            pets=pets
        )

        plan: HatchPlan = plan_maker.make_plan()
        expected_plan = HatchPlan() \
            .add(egg=Egg(hatchable1), potion=HatchPotion("Vampire")) \
            .add(egg=Egg(hatchable2), potion=HatchPotion("Vampire")) \
            .add(egg=Egg(hatchable3), potion=HatchPotion("Vampire"))

        assert plan == expected_plan
