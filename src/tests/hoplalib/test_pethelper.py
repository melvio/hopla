#!/usr/bin/env python3
import pytest
import random

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.pethelper import Pet, InvalidPet, PetData

_SAMPLE_SIZE = 50
"""
Sample size to use for pytest.mark.parameterize when unittests become slow
"""


class TestPetInit:
    def test_init_raises_invalid_pet_name(self):
        with pytest.raises(InvalidPet) as execinfo:
            invalid_pet_name = "INVALID_PET"
            Pet(invalid_pet_name)

        err_msg = str(execinfo.value)
        assert invalid_pet_name in err_msg
        assert f"an issue at {GlobalConstants.NEW_ISSUE_URL}" in err_msg

    @pytest.mark.parametrize(
        "pet_name",
        # Testing all pets takes too long (approx. 2 seconds), so we sample.
        random.sample(PetData.pet_names, k=_SAMPLE_SIZE))
    def test_init_valid_pet_name_ok(self, pet_name: str):
        pet = Pet(pet_name=pet_name)
        assert pet.pet_name == pet_name

    @pytest.mark.parametrize(
        "invalid_feed_status",
        [-10, -2, 1, 3, 51, 100]
    )
    def test_init_raises_invalid_feeding_status_fail(self, invalid_feed_status: int):
        with pytest.raises(InvalidPet) as execinfo:
            Pet("PandaCub-IcySnow", feeding_status=invalid_feed_status)

        err_msg = str(execinfo.value)
        assert f"feeding_status={invalid_feed_status}" in err_msg

    @pytest.mark.parametrize(
        "valid_feed_status",
        [5, 10, 20, -1, 49]
    )
    def test_init_sets_valid_feeding_status_ok(self, valid_feed_status: int):
        pet = Pet("LionCub-Sunset", feeding_status=valid_feed_status)

        assert valid_feed_status == pet.feeding_status


class TestPetFunctions:
    PET_NAME = "Fox-Ember"

    @pytest.mark.parametrize(
        "feeding_status,expected_percentage",
        [(-1, 100), (5, 10), (7, 14), (48, 96)]
    )
    def test_feeding_status_to_percentage_ok(self, feeding_status: int,
                                             expected_percentage: int):
        pet = Pet("LionCub-AutumnLeaf", feeding_status=feeding_status)
        assert pet.feeding_status_to_percentage() == expected_percentage

    @pytest.mark.parametrize(
        "feeding_status,partial_expected_message", [
            (-1, f"can't feed self.pet_name='{PET_NAME}'"),
            (5, f"Cannot determine if self.pet_name='{PET_NAME}"),
            (20, f"pet_name='{PET_NAME}' can be fed")
        ]
    )
    def test_feeding_status_explanation_ok(self, feeding_status: int,
                                           partial_expected_message: str):
        pet = Pet(TestPetFunctions.PET_NAME, feeding_status=feeding_status)

        assert partial_expected_message in pet.feeding_status_explanation()

    @pytest.mark.parametrize(
        "pet_name,expected_favorite_food", [
            ("Wolf-Base", "Meat"),
            ("FlyingPig-CottonCandyPink", "CottonCandyPink"),
            ("PandaCub-CottonCandyBlue", "CottonCandyBlue"),
            ("TigerCub-Golden", "Honey"),
            ("Fox-Red", "Strawberry"),
            ("BearCub-White", "Milk"),
            ("Dragon-Desert", "Potatoe")
        ]
    )
    def test_favorite_food_for_gen1_pets_ok(self, pet_name: str,
                                            expected_favorite_food: str):
        pet = Pet(pet_name)
        assert pet.favorite_food() == expected_favorite_food

    @pytest.mark.parametrize(
        "pet_name", random.sample(PetData.pet_names, k=_SAMPLE_SIZE)
    )
    def test_favorite_food_generic_case_ok(self, pet_name: str):
        pet = Pet(pet_name)

        if pet.is_from_drop_hatching_potions():
            # These pets have a favorite food
            assert pet.favorite_food() != "Any"

            alternative_food = "SomeFakeFood"
            result = pet.favorite_food(default_value_when_no_favorite_food=alternative_food)
            assert result != alternative_food
        else:
            # These pets like every food
            assert pet.favorite_food() == "Any"

            alternative_food = "Meat"
            result = pet.favorite_food(default_value_when_no_favorite_food=alternative_food)
            assert result == alternative_food

    @pytest.mark.parametrize(
        "pet_name,is_gen1_expected",
        [
            ("Wolf-Base", True),
            ("FlyingPig-CottonCandyPink", True),
            ("PandaCub-CottonCandyBlue", True),
            ("TigerCub-Golden", True),
            ("Fox-Red", True),
            ("BearCub-White", True),
            ("Dragon-Desert", True),
            ("Cactus-Amber", False),
            ("BearCub-Frost", False),
            ("Butterfly-Red", False)
        ]
    )
    def test_is_generation1_pet_ok(self, pet_name, is_gen1_expected):
        pet = Pet(pet_name)
        assert pet.is_generation1_pet() is is_gen1_expected

    @pytest.mark.parametrize(
        "pet_name",
        random.sample(PetData.generation1_pet_names + PetData.quest_pet_names,
                      k=_SAMPLE_SIZE)
    )
    def test_has_only1_favorite_food_true(self, pet_name):
        pet = Pet(pet_name=pet_name)
        assert pet.has_only1_type_of_favorite_food()

    @pytest.mark.parametrize(
        "pet_name",
        random.sample(PetData.magic_potion_pet_names, k=_SAMPLE_SIZE)
    )
    def test_has_only1_favorite_food_false(self, pet_name):
        pet = Pet(pet_name=pet_name)
        assert pet.has_only1_type_of_favorite_food() is False
