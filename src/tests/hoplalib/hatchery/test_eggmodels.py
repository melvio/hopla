#!/usr/bin/env python3
import random
from typing import List

import click
import pytest

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.eggmodels import Egg, EggCollection, EggException
from hopla.hoplalib.hatchery.egg_data import EggData
from hopla.hoplalib.hatchery.hatchpotion_data import HatchPotionData
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchPotion

_SAMPLE_SIZE = 9


class TestEgg:
    def test__init__invalid_name_fail(self):
        name = "InvalidName"
        with pytest.raises(EggException) as exec_info:
            Egg(name)

        assert str(exec_info.value).startswith(f"{name} is not a valid egg name.")
        assert exec_info.errisinstance((YouFoundABugRewardError, click.ClickException))

    @pytest.mark.parametrize(
        "egg_name,quantity",
        list(zip(random.sample(EggData.egg_names, k=_SAMPLE_SIZE),
                 range(-_SAMPLE_SIZE, 0)))
    )
    def test__init__invalid_quantity_fail(self, egg_name: str, quantity: int):
        with pytest.raises(EggException) as exec_info:
            Egg(egg_name, quantity=quantity)

        assert str(exec_info.value).startswith(f"{quantity} is below 0.")
        assert exec_info.errisinstance((YouFoundABugRewardError, click.ClickException))

    @pytest.mark.parametrize("egg1,egg2,expected_equals", [
        (Egg("Horse"), Egg("Horse"), True),
        (Egg("Seahorse", quantity=1), Egg("Seahorse"), True),
        (Egg("Snake", quantity=1), Egg("Snake", quantity=2), False),
        (Egg("Whale"), Egg("Rat"), False),
        (Egg("Rooster", quantity=0), Egg("TRex", quantity=0), False),
        (Egg("Penguin", quantity=1), Egg("Owl", quantity=4), False),
    ])
    def test__eq__(self, egg1: Egg, egg2: Egg, expected_equals: bool):
        assert (egg1 == egg2) is expected_equals

    def test__repr__(self):
        name, quantity = "Dolphin", 9
        egg = Egg(name, quantity=quantity)

        result: str = repr(egg)

        assert result == f"Egg({name}: {quantity})"

    @pytest.mark.parametrize("standard_egg_name", ["Wolf", "Fox", "FlyingPig", "Dragon"])
    def test_is_standard_egg(self, standard_egg_name: str):
        egg = Egg(standard_egg_name)

        assert egg.is_standard_egg() is True
        assert egg.is_quest_egg() is False

    @pytest.mark.parametrize("quest_egg_name", [
        "Dolphin", "Gryphon", "Deer", "Egg", "Seahorse", "Parrot"
    ])
    def test_is_quest_egg(self, quest_egg_name: str):
        egg = Egg(quest_egg_name)

        assert egg.is_standard_egg() is False
        assert egg.is_quest_egg() is True

    @pytest.mark.parametrize(
        "egg_name,potion_name",
        list(zip(EggData.drop_egg_names,
                 HatchPotionData.hatch_potion_names))
    )
    def test_can_be_hatched_by_standard_egg_true(self, egg_name: str,
                                                 potion_name: str):
        egg = Egg(egg_name)
        potion = HatchPotion(potion_name)

        # standard eggs can be hatched by any potion
        assert egg.can_be_hatched_by(potion) is True

    @pytest.mark.parametrize(
        "egg_name,potion_name",
        list(zip(EggData.quest_egg_names,
                 HatchPotionData.drop_hatch_potion_names))
    )
    def test_can_be_hatched_by_magic_egg_drop_potion_true(self,
                                                          egg_name: str,
                                                          potion_name: str):
        egg = Egg(egg_name)
        potion = HatchPotion(potion_name)

        # quest eggs can be hatched by standard potion
        assert egg.can_be_hatched_by(potion) is True

    @pytest.mark.parametrize(
        "egg_name,potion_name",
        list(zip(
            random.sample(EggData.quest_egg_names, k=_SAMPLE_SIZE),
            random.sample(HatchPotionData.non_drop_hatch_potion_names, k=_SAMPLE_SIZE)
        ))
    )
    def test_can_be_hatched_by_magic_egg_non_drop_potion_false(self,
                                                               egg_name: str,
                                                               potion_name: str):
        egg = Egg(egg_name)
        potion = HatchPotion(potion_name)

        # quest eggs cannot be hatched by non standard potion
        assert egg.can_be_hatched_by(potion) is False


class TestEggCollection:
    def test__init__empty__ok(self):
        collection = EggCollection()
        assert collection == EggCollection({})
        assert len(collection) == 0

    def test__init__ok(self):
        collection = EggCollection({"Wolf": 0, "Whale": 42, "Horse": 2})

        assert len(collection) == 3
        assert collection["Wolf"] == Egg("Wolf", quantity=0)
        assert collection["Whale"] == Egg("Whale", quantity=42)
        assert collection["Horse"] == Egg("Horse", quantity=2)

    def test__eq__(self):
        assert EggCollection() == EggCollection()
        assert EggCollection() == EggCollection({})
        assert EggCollection({"Cow": 1}) == EggCollection({"Cow": 1})
        assert EggCollection({"Cow": 1}) != EggCollection({"Cow": 2})
        assert EggCollection({"Cow": 1}) != EggCollection({"Rat": 1})
        assert EggCollection() != EggCollection({"Ferret": 1})

    def test_values_ok(self):
        collection = EggCollection({"Wolf": 1, "Whale": 41, "Horse": 2})

        generator = collection.values()
        assert next(generator) == Egg("Wolf", quantity=1)
        assert next(generator) == Egg("Whale", quantity=41)
        assert next(generator) == Egg("Horse", quantity=2)
        with pytest.raises(StopIteration):
            _ = next(generator)

    def test_values_as_list_ok(self):
        collection = EggCollection({"Wolf": 1, "Whale": 41, "Horse": 2})

        result: List[Egg] = list(collection.values())

        expected: List[Egg] = [
            Egg("Wolf", quantity=1), Egg("Whale", quantity=41), Egg("Horse", quantity=2)
        ]
        assert result == expected

    def test__iter__ok(self):
        collection = EggCollection({"Wolf": 1, "Whale": 42, "Horse": 2})

        iterator = iter(collection)

        assert next(iterator) == "Wolf"
        assert next(iterator) == "Whale"
        assert next(iterator) == "Horse"
        with pytest.raises(StopIteration):
            next(iterator)

    def test_remove_egg_not_available_faile(self):
        collection = EggCollection({"Whale": 1})

        not_found_egg = "Unicorn"
        with pytest.raises(EggException) as exec_info:
            collection.remove_egg(Egg(not_found_egg))

        expected_msg = f"{not_found_egg} was not in the collection "
        assert str(exec_info.value).startswith(expected_msg)

    def test_remove_egg_ok(self):
        egg1_name, egg1_quantity = "Wolf", 1
        egg2_name, egg2_quantity = "Whale", 42
        egg3_name, egg3_quantity = "Horse", 2
        collection = EggCollection(
            {egg1_name: egg1_quantity, egg2_name: egg2_quantity, egg3_name: egg3_quantity}
        )

        collection.remove_egg(Egg(egg1_name))
        collection.remove_egg(Egg(egg2_name))
        collection.remove_egg(Egg(egg3_name))

        assert collection[egg1_name] == Egg(egg1_name, quantity=egg1_quantity - 1)
        assert collection[egg2_name] == Egg(egg2_name, quantity=egg2_quantity - 1)
        assert collection[egg3_name] == Egg(egg3_name, quantity=egg3_quantity - 1)

    def test_get_standard_egg_collection_ok(self):
        egg1_name, egg1_quantity = "Wolf", 1
        egg2_name, egg2_quantity = "Whale", 42  # quest egg
        egg3_name, egg3_quantity = "Fox", 0
        egg4_name, egg4_quantity = "PandaCub", 69
        collection = EggCollection({
            egg1_name: egg1_quantity,
            egg2_name: egg2_quantity,
            egg3_name: egg3_quantity,
            egg4_name: egg4_quantity
        })

        result: EggCollection = collection.get_standard_egg_collection()

        expected = EggCollection({
            egg1_name: egg1_quantity, egg3_name: egg3_quantity, egg4_name: egg4_quantity
        })
        assert result == expected

    def test_get_quest_egg_collection_ok(self):
        egg1_name, egg1_quantity = "Wolf", 1  # not quest egg
        egg2_name, egg2_quantity = "Whale", 42
        egg3_name, egg3_quantity = "Horse", 0
        egg4_name, egg4_quantity = "Axolotl", 69
        collection = EggCollection({
            egg1_name: egg1_quantity,
            egg2_name: egg2_quantity,
            egg3_name: egg3_quantity,
            egg4_name: egg4_quantity
        })

        result: EggCollection = collection.get_quest_egg_collection()

        expected = EggCollection({
            egg2_name: egg2_quantity, egg3_name: egg3_quantity, egg4_name: egg4_quantity
        })
        assert result == expected
