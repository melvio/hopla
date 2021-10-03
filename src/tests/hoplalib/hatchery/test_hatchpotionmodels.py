#!/usr/bin/env python3
import random

import click
import pytest

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.hatchdata import HatchingPotionData
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchingPotion, HatchingPotionCollection, \
    HatchingPotionException

_SAMPLE_SIZE = 10


class TestHatchingPotion:
    def test__init__invalid_name_fail(self):
        name = "InvalidName"
        with pytest.raises(HatchingPotionException) as exec_info:
            HatchingPotion(name, quantity=1)

        assert str(exec_info.value).startswith(f"{name} is not a valid hatching potion name.")
        assert exec_info.errisinstance((YouFoundABugRewardError, click.ClickException))

    @pytest.mark.parametrize(
        "potion_name,quantity",
        list(zip(random.sample(HatchingPotionData.hatching_potion_names, k=_SAMPLE_SIZE),
                 range(-_SAMPLE_SIZE, 0)))
    )
    def test__init__invalid_quantity_fail(self, potion_name: str, quantity: int):
        with pytest.raises(HatchingPotionException) as exec_info:
            HatchingPotion(potion_name, quantity=quantity)

        assert str(exec_info.value).startswith(f"{quantity} is below 0.")
        assert exec_info.errisinstance((YouFoundABugRewardError, click.ClickException))

    @pytest.mark.parametrize(
        "potion_name,quantity",
        list(zip(random.sample(HatchingPotionData.hatching_potion_names, k=_SAMPLE_SIZE),
                 range(0, _SAMPLE_SIZE)))
    )
    def test__repr__ok(self, potion_name: str, quantity: int):
        potion = HatchingPotion(potion_name, quantity=quantity)

        result: str = repr(potion)

        assert result == f"HatchingPotion({potion_name}: {quantity})"

    @pytest.mark.parametrize("potion_name,quantity", [
        ("Base", 10),
        ("CottonCandyBlue", 1),
        ("Golden", 0),
    ])
    def test_is_standard_potion(self, potion_name: str, quantity: int):
        potion = HatchingPotion(potion_name, quantity=quantity)

        assert potion.is_standard_hatching_potion() is True
        assert potion.is_magic_hatching_potion() is False
        assert potion.is_wacky_hatching_potion() is False

    @pytest.mark.parametrize("potion_name,quantity", [
        ("BirchBark", 10),
        ("Windup", 1),
        ("Vampire", 0),
        ("Ruby", 9),
        ("Amber", 69),
        ("MossyStone", 42),
        ("SolarSystem", 9001),
    ])
    def test_is_magic_potion(self, potion_name: str, quantity: int):
        potion = HatchingPotion(potion_name, quantity=quantity)

        assert potion.is_standard_hatching_potion() is False
        assert potion.is_magic_hatching_potion() is True
        assert potion.is_wacky_hatching_potion() is False

    @pytest.mark.parametrize("potion_name,quantity", [
        ("Veggie", 10),
        ("Dessert", 0),
    ])
    def test_is_wacky_hatching_potion(self, potion_name: str, quantity: int):
        potion = HatchingPotion(potion_name, quantity=quantity)

        assert potion.is_standard_hatching_potion() is False
        assert potion.is_magic_hatching_potion() is False
        assert potion.is_wacky_hatching_potion() is True


class TestHatchingPotionCollection:
    def test__init__empty_ok(self):
        collection = HatchingPotionCollection()
        assert len(collection) == 0

    def test__init__ok(self):
        potion_dict = {"Base": 0, "Moonglow": 42, "Sunset": 2}

        collection = HatchingPotionCollection(potion_dict)

        assert collection["Base"] == HatchingPotion("Base", quantity=0)
        assert collection["Moonglow"] == HatchingPotion("Moonglow", quantity=42)
        assert collection["Sunset"] == HatchingPotion("Sunset", quantity=2)

    def test__iter__ok(self):
        collection = HatchingPotionCollection({"Base": 1, "Moonglow": 42, "Sunset": 2})

        iterator = iter(collection)

        assert next(iterator) == "Base"
        assert next(iterator) == "Moonglow"
        assert next(iterator) == "Sunset"
        with pytest.raises(StopIteration):
            next(iterator)

    def test__getitem__ok(self):
        collection = HatchingPotionCollection({"Base": 1, "Moonglow": 42, "Sunset": 0})

        assert collection["Base"] == HatchingPotion("Base", quantity=1)
        assert collection["Moonglow"] == HatchingPotion("Moonglow", quantity=42)
        assert collection["Sunset"] == HatchingPotion("Sunset", quantity=0)

    def test_remove_hatching_potion_ok(self):
        potion1_quantity = 3
        potion2_quantity = 42
        potion3_name, potion3_quantity = "Sunset", 1
        collection = HatchingPotionCollection({
            "Base": potion1_quantity,
            "Moonglow": potion2_quantity,
            potion3_name: potion3_quantity
        })

        collection.remove_hatching_potion(HatchingPotion("Base"))
        collection.remove_hatching_potion(HatchingPotion("Moonglow"))
        collection.remove_hatching_potion(HatchingPotion(potion3_name))

        assert collection["Base"] == HatchingPotion("Base",
                                                    quantity=potion1_quantity - 1)
        assert collection["Moonglow"] == HatchingPotion("Moonglow",
                                                        quantity=potion2_quantity - 1)
        assert collection[potion3_name] == HatchingPotion(potion3_name,
                                                          quantity=potion3_quantity - 1)

    def test_remove_hatching_potion_not_available_faile(self):
        collection = HatchingPotionCollection({"Base": 1})

        not_found_potion_name = "Moonglow"
        with pytest.raises(HatchingPotionException) as exec_info:
            collection.remove_hatching_potion(HatchingPotion(not_found_potion_name))

        expected_msg = f"{not_found_potion_name} was not in the collection "
        assert str(exec_info.value).startswith(expected_msg)
