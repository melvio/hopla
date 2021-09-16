#!/usr/bin/env python3
import pytest
import random

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.zoo.petmodels import FeedingStatus, InvalidFeedingStatus, Pet, InvalidPet
from hopla.hoplalib.zoo.petdata import PetData

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
        random.sample(PetData.pet_names, k=_SAMPLE_SIZE)
    )
    def test_init_valid_pet_name_ok(self, pet_name: str):
        pet = Pet(pet_name=pet_name)
        assert pet.pet_name == pet_name

    @pytest.mark.parametrize(
        "invalid_feed_status",
        [-10, -2, 1, 3, 51, 100]
    )
    def test_init_raises_invalid_feeding_status_fail(self, invalid_feed_status: int):
        with pytest.raises(InvalidFeedingStatus) as execinfo:
            feeding_status = FeedingStatus(invalid_feed_status)
            Pet("PandaCub-IcySnow", feeding_status=feeding_status)

        err_msg = str(execinfo.value)
        assert f"feeding_status={int(invalid_feed_status)}" in err_msg

    @pytest.mark.parametrize(
        "valid_feed_status",
        [5, 10, 20, -1, 49]
    )
    def test_init_sets_valid_feeding_status_ok(self, valid_feed_status: int):
        feeding_status = FeedingStatus(valid_feed_status)
        pet = Pet("LionCub-Sunset", feeding_status=feeding_status)

        assert valid_feed_status == int(pet.feeding_status)


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


class TestFavoriteFood:
    @pytest.mark.parametrize(
        "pet_name,expected_favorite_food", [
            ("Wolf-Base", "Meat"),
            ("FlyingPig-CottonCandyPink", "CottonCandyPink"),
            ("PandaCub-CottonCandyBlue", "CottonCandyBlue"),
            ("TigerCub-Golden", "Honey"),
            ("Fox-Red", "Strawberry"),
            ("BearCub-White", "Milk"),
            ("Dragon-Desert", "Potatoe"),
            ("Robot-Shade", "Chocolate"),
            ("Dolphin-Skeleton", "Fish")
        ]
    )
    def test_favorite_food_for_pets_with_favorite_food_ok(self, pet_name: str,
                                                          expected_favorite_food: str):
        pet = Pet(pet_name)
        assert pet.favorite_food() == expected_favorite_food

    @pytest.mark.parametrize(
        "pet_name", random.sample(PetData.only_1favorite_food_pet_names, k=_SAMPLE_SIZE)
    )
    def test_favorite_food_single_favorite_food_ok(self, pet_name: str):
        pet = Pet(pet_name)
        alternative_food = "SomeFakeFood"

        assert "Any" != pet.favorite_food()
        assert alternative_food != pet.favorite_food(
            default_value_for_all_favorite_food=alternative_food
        )
        assert "Unfeedable" != pet.favorite_food(
            default_value_for_unfeedable=alternative_food
        )

    @pytest.mark.parametrize(
        # only magic potion pets like all foods
        "pet_name", random.sample(PetData.magic_potion_pet_names, k=_SAMPLE_SIZE)
    )
    def test_favorite_food_multiple_favorite_food_ok(self, pet_name: str):
        pet = Pet(pet_name)

        alternative_food = "Whatever"
        default_value_for_all_favorite_food_ok_pets = "Any"
        assert alternative_food == pet.favorite_food(
            default_value_for_all_favorite_food=alternative_food
        )
        assert default_value_for_all_favorite_food_ok_pets == pet.favorite_food(
            default_value_for_unfeedable=alternative_food
        )
        assert default_value_for_all_favorite_food_ok_pets == pet.favorite_food()

    @pytest.mark.parametrize(
        # only magic potion pets like all foods
        "pet_name", PetData.unfeedable_pet_names
    )
    def test_favorite_food_for_unfeedable_pets(self, pet_name: str):
        pet = Pet(pet_name)

        alternative_food = "Whatever"
        default_value_for_unfeedable_pets = "Unfeedable"
        assert default_value_for_unfeedable_pets == pet.favorite_food(
            default_value_for_all_favorite_food=alternative_food
        )
        assert alternative_food == pet.favorite_food(default_value_for_unfeedable=alternative_food)
        assert default_value_for_unfeedable_pets == pet.favorite_food()


class TestIsFavoriteFood:
    @pytest.mark.parametrize(
        "pet_name,food_name",
        # we use choices here because both groups are smaller than
        # the specified k
        zip(random.choices(PetData.unfeedable_pet_names, k=_SAMPLE_SIZE),
            random.choices(PetData.drop_food_names, k=_SAMPLE_SIZE))
    )
    def test_is_favorite_food_false_because_unfeedable(self, pet_name: str,
                                                       food_name: str):
        pet = Pet(pet_name)
        assert pet.is_favorite_food(food_name) is False

    @pytest.mark.parametrize(
        "pet_name,food_name",
        zip(random.sample(PetData.magic_potion_pet_names, k=_SAMPLE_SIZE),
            random.choices(PetData.drop_food_names, k=_SAMPLE_SIZE))
    )
    def test_is_favorite_food_true_because_likes_all_food(self,
                                                          pet_name: str,
                                                          food_name: str):
        assert Pet(pet_name).is_favorite_food(food_name)

    @pytest.mark.parametrize(
        "pet_name,food_name,expected_result", [
            ("Fox-Red", "Strawberry", True),
            ("Fox-Red", "Milk", False),
            ("Parrot-Desert", "Potatoe", True),
            ("Parrot-Base", "Potatoe", False),
            ("Hippo-Golden", "Honey", True),
            ("Hippo-Golden", "CottonCandyBlue", False),
        ]
    )
    def test_is_favorite_food_for_hatching_pets(self,
                                                pet_name: str,
                                                food_name: str,
                                                expected_result: bool):
        pet = Pet(pet_name)
        result = pet.is_favorite_food(food_name)
        assert result is expected_result


class TestOtherPetFunctions:
    """ Test class for Pet functions that aren't covered elsewhere """
    PET_NAME = "Fox-Ember"

    @pytest.mark.parametrize(
        "feeding_status,partial_expected_message", [
            (-1, f"can't feed self.pet_name='{PET_NAME}' you only have the mount"),
            (5, f"Cannot determine if self.pet_name='{PET_NAME}' can be fed"),
            (20, f"pet_name='{PET_NAME}' can be fed")
        ]
    )
    def test_feeding_status_explanation_ok(self, feeding_status: int,
                                           partial_expected_message: str):
        feeding_status = FeedingStatus(feeding_status)
        pet = Pet(TestOtherPetFunctions.PET_NAME, feeding_status=feeding_status)

        result_explanation = pet.feeding_status_explanation()

        assert partial_expected_message in result_explanation

    @pytest.mark.parametrize(
        "unfeedable_pet_name", [
            "Fox-Veteran", "JackOLantern-Glow", "JackOLantern-RoyalPurple", "MantisShrimp-Base",
            "Gryphon-Gryphatrice", "PandaCub-Dessert", "LionCub-Veggie", "LionCub-Dessert",
            "Fox-Veggie", "Fox-Dessert",
        ]
    )
    def test_feeding_status_unfeedable_pet(self, unfeedable_pet_name: str):
        pet = Pet(unfeedable_pet_name)

        result_explanation = pet.feeding_status_explanation()

        assert pet.pet_name in result_explanation
        assert "can't be fed because it is special" in result_explanation

    @pytest.mark.parametrize(
        "pet_name,is_gen1_expected", [
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
    def test_has_just_1_favorite_food_true(self, pet_name):
        pet = Pet(pet_name=pet_name)
        assert pet.has_just_1_favorite_food()

    @pytest.mark.parametrize(
        "pet_name",
        random.sample(PetData.magic_potion_pet_names, k=_SAMPLE_SIZE)
    )
    def test_has_just_1_favorite_food_false(self, pet_name):
        pet = Pet(pet_name=pet_name)
        assert pet.has_just_1_favorite_food() is False

    @pytest.mark.parametrize(
        "pet_name,likes_all_food_expected", [
            ("Fox-Golden", False),
            ("LionCub-Holly", True),
            ("PandaCub-Cupid", True),
            ("Octopus-Red", False),
            ("Seahorse-CottonCandyBlue", False)
        ]
    )
    def test_likes_all_food(self, pet_name: str,
                            likes_all_food_expected: bool):
        pet = Pet(pet_name)

        result = pet.likes_all_food()

        assert result is likes_all_food_expected

    @pytest.mark.parametrize(
        "pet_name,expected_from_drop_hatching_potion", [
            ("Fox-Golden", True),
            ("Dragon-Shade", True),
            ("LionCub-Holly", False),
            ("PandaCub-Cupid", False),
            ("Octopus-Red", True),
            ("Cheetah-CottonCandyPink", True),
            ("Seahorse-CottonCandyBlue", True),
            ("Unicorn-Skeleton", True),
            ("MagicalBee-Base", False),  # although -Base postfix, this is a world boss reward
            ("Phoenix-Base", False),  # although -Base postfix, this is a world boss reward
            ("Turkey-Base", False),  # although -Base postfix, this is a event sequence reward
            ("Gryphon-Gryphatrice", False),
        ]
    )
    def test_is_from_drop_hatching_potion(self, pet_name: str,
                                          expected_from_drop_hatching_potion: bool):
        pet = Pet(pet_name)

        result = pet.is_from_drop_hatching_potions()

        assert result is expected_from_drop_hatching_potion

    def test___repr__(self):
        pet_name = "Fox-Shadow"
        feeding_status = FeedingStatus(10)
        pet = Pet(pet_name, feeding_status=feeding_status)

        result = str(pet)

        expected = f"Pet(self.pet_name='{pet_name}', self.feeding_status={feeding_status})"
        assert result == expected
