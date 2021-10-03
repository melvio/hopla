#!/usr/bin/env python3
import random
from typing import List

import pytest
from click import ClickException

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.zoo.fooddata import FoodData
from hopla.hoplalib.zoo.foodmodels import FeedStatus, InvalidFeedStatus
from hopla.hoplalib.zoo.petdata import PetData
from hopla.hoplalib.zoo.petmodels import InvalidPet, InvalidPetMountPair, Mount, Pet, PetMountPair

_SAMPLE_SIZE = 25
"""
Sample size to use for pytest.mark.parameterize when unittests become slow
"""


class TestPet:
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
            assert pet.name == pet_name

        @pytest.mark.parametrize("invalid_feed_status", [-10, -2, 1, 3, 51, 100])
        def test_init_raises_invalid_feed_status_fail(self, invalid_feed_status: int):
            with pytest.raises(InvalidFeedStatus) as execinfo:
                feed_status = FeedStatus(invalid_feed_status)
                Pet("PandaCub-IcySnow", feed_status=feed_status)

            err_msg = str(execinfo.value)
            assert f"feed_status={int(invalid_feed_status)}" in err_msg

        @pytest.mark.parametrize("valid_feed_status", [5, 10, 20, -1, 49])
        def test_init_sets_valid_feed_status_ok(self, valid_feed_status: int):
            feed_status = FeedStatus(valid_feed_status)
            pet = Pet("LionCub-Sunset", feed_status=feed_status)

            assert valid_feed_status == int(pet.feed_status)

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
            assert alternative_food == pet.favorite_food(
                default_value_for_unfeedable=alternative_food)
            assert default_value_for_unfeedable_pets == pet.favorite_food()

    class TestIsFavoriteFood:

        @pytest.mark.parametrize(
            "pet_name,food_name",
            # we use choices here because both groups are smaller than
            # the specified k
            zip(random.choices(PetData.unfeedable_pet_names, k=_SAMPLE_SIZE),
                random.choices(FoodData.drop_food_names, k=_SAMPLE_SIZE))
        )
        def test_is_favorite_food_false_because_unfeedable(self, pet_name: str,
                                                           food_name: str):
            pet = Pet(pet_name)
            assert pet.is_favorite_food(food_name) is False

        @pytest.mark.parametrize(
            "pet_name,food_name",
            zip(random.sample(PetData.magic_potion_pet_names, k=_SAMPLE_SIZE),
                random.choices(FoodData.drop_food_names, k=_SAMPLE_SIZE))
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
        def test_is_favorite_food_for_hatch_pets(self,
                                                 pet_name: str,
                                                 food_name: str,
                                                 expected_result: bool):
            pet = Pet(pet_name)
            result = pet.is_favorite_food(food_name)
            assert result is expected_result

    class TestOtherPetFunctions:
        """ Test class for Pet functions that aren't covered elsewhere """
        PET_NAME = "Fox-Ember"

        def test___repr__(self):
            pet_name = "Fox-Shadow"
            feed_status = FeedStatus(10)
            pet = Pet(pet_name, feed_status=feed_status)

            result = str(pet)

            expected = f"Pet({pet_name}: {feed_status})"
            assert result == expected

        @pytest.mark.parametrize(
            "feed_status,partial_expected_message", [
                (-1, f"can't feed self.name='{PET_NAME}' you only have the mount"),
                (0, f"You released {PET_NAME}, so you cannot feed it"),
                (5, f"Cannot determine if self.name='{PET_NAME}' can be fed"),
                (20, f"name='{PET_NAME}' can be fed")
            ]
        )
        def test_feed_status_explanation_ok(self, feed_status: int,
                                            partial_expected_message: str):
            feed_status = FeedStatus(feed_status)
            pet = Pet(TestPet.TestOtherPetFunctions.PET_NAME, feed_status=feed_status)

            result_explanation: str = pet.feed_status_explanation()

            assert partial_expected_message in result_explanation

        @pytest.mark.parametrize(
            "unfeedable_pet_name", [
                "Fox-Veteran", "JackOLantern-Glow", "JackOLantern-RoyalPurple",
                "MantisShrimp-Base",
                "Gryphon-Gryphatrice", "PandaCub-Dessert", "LionCub-Veggie", "LionCub-Dessert",
                "Fox-Veggie", "Fox-Dessert",
            ]
        )
        def test_feed_status_unfeedable_pet(self, unfeedable_pet_name: str):
            pet = Pet(unfeedable_pet_name)

            result_explanation: str = pet.feed_status_explanation()

            assert f"{pet.name} is an unfeedable pet." == result_explanation

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
            "pet_name,expected_from_drop_hatch_potion", [
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
        def test_is_from_drop_hatch_potion(self, pet_name: str,
                                           expected_from_drop_hatch_potion: bool):
            pet = Pet(pet_name)

            result = pet.is_from_drop_hatch_potions()

            assert result is expected_from_drop_hatch_potion

        @pytest.mark.parametrize(
            "pet_name", random.sample(PetData.quest_pet_names, k=_SAMPLE_SIZE)
        )
        def test_is_quest_pet_true(self, pet_name: str):
            pet = Pet(pet_name)
            assert pet.is_quest_pet() is True

        @pytest.mark.parametrize(
            "pet_name",
            random.sample(PetData.generation1_pet_names + PetData.magic_potion_pet_names,
                          k=_SAMPLE_SIZE)
        )
        def test_is_quest_pet_false(self, pet_name: str):
            pet = Pet(pet_name)
            assert pet.is_quest_pet() is False

        @pytest.mark.parametrize(
            "pet_name",
            random.sample(PetData.magic_potion_pet_names, k=_SAMPLE_SIZE)
        )
        def test_is_magic_hatch_potion_true(self, pet_name: str):
            pet = Pet(pet_name)
            assert pet.is_magic_hatch_pet() is True

        @pytest.mark.parametrize(
            "pet_name",
            random.sample(PetData.generation1_pet_names + PetData.rare_pet_names +
                          PetData.quest_pet_names,
                          k=_SAMPLE_SIZE)
        )
        def test_is_magic_hatch_potion_false(self, pet_name: str):
            pet = Pet(pet_name)
            assert pet.is_magic_hatch_pet() is False

        @pytest.mark.parametrize(
            "pet,food_name,expected_times", [
                (Pet("Hedgehog-Shade", feed_status=FeedStatus(10)), "Chocolate", 8),
                (Pet("Hedgehog-Shade", feed_status=FeedStatus(10)), "Milk", 20),
                (Pet("Egg-Base"), "Meat", 9),
                (Pet("Egg-Zombie"), "CottonCandyPink", 23),
                (Pet("Egg-Base", feed_status=FeedStatus(40)), "Meat", 2),
                (Pet("Egg-Base", feed_status=FeedStatus(44)), "Meat", 2),
                (Pet("Egg-Golden", feed_status=FeedStatus(47)), "Fish", 2),
            ]
        )
        def test_required_food_items_until_mount(self, pet: Pet,
                                                 food_name: str,
                                                 expected_times: int):
            times_result: int = pet.required_food_items_until_mount(food_name)

            assert times_result == expected_times


class TestMount:

    @pytest.mark.parametrize(
        "mount,expected", [
            (Mount("Wolf-Veteran", availability_status=True), "Mount(Wolf-Veteran: True)"),
            (Mount("Monkey-Shade", availability_status=None), "Mount(Monkey-Shade: None)")
        ]
    )
    def test__repr__(self, mount: Mount, expected: str):
        result: str = repr(mount)
        assert result == expected

    @pytest.mark.parametrize("mount,expected_available", [
        (Mount("Aether-Invisible", availability_status=True), True),
        (Mount("BearCub-Celestial", availability_status=False), False),
        (Mount("Cactus-Ember", availability_status=None), False)
    ])
    def test_is_available_ok(self, mount: Mount, expected_available: bool):
        assert mount.is_available() is expected_available


class TestPetMountPair:
    empty_pair = PetMountPair(pet=None, mount=None)

    phoenix_pet_only_pair = PetMountPair(pet=Pet("Phoenix-Base", feed_status=FeedStatus(5)),
                                         mount=None)

    phoenix_mount_only_pair = PetMountPair(pet=None,
                                           mount=Mount("Phoenix-Base", availability_status=True))

    mount_available_pairs: List[PetMountPair] = [
        # only mount
        PetMountPair(pet=Pet("Owl-Shade", feed_status=FeedStatus(-1)),
                     mount=Mount("Owl-Shade", availability_status=True)),
        # pet is there, and mount as well
        PetMountPair(pet=Pet("Egg-White", feed_status=FeedStatus(5)),
                     mount=Mount("Egg-White", availability_status=True)),
        phoenix_mount_only_pair
    ]

    unfeedable_pairs: List[PetMountPair] = [
        # no pets
        empty_pair, phoenix_mount_only_pair,
        # cannot feed pet if there is a mount
        *mount_available_pairs,
        # released pet
        PetMountPair(pet=Pet("Wolf-Base", feed_status=FeedStatus(0)),
                     mount=None),
        # unfeedable pet
        phoenix_pet_only_pair,
        # no corresponding pet for this mount
        PetMountPair(pet=None, mount=Mount("Aether-Invisible", availability_status=True))
    ]

    feedable_pairs: List[PetMountPair] = [
        # only pet
        PetMountPair(pet=Pet("Rat-CottonCandyBlue", feed_status=FeedStatus(10)),
                     mount=None),
        # mount was released
        PetMountPair(pet=Pet("Rat-CottonCandyPink", feed_status=FeedStatus(5)),
                     mount=Mount("Rat-CottonCandyPink", availability_status=None)),
    ]

    @pytest.mark.parametrize("pair", feedable_pairs + unfeedable_pairs)
    def test_init__ok(self, pair: PetMountPair):
        pet: Pet = pair.pet
        mount: Mount = pair.mount

        if pet is not None:
            assert pet.name is not None
            assert pet.feed_status is not None

        if mount is not None:
            assert mount.name is not None
            assert mount.is_available() in [True, False, None]

    def test__init__pet_mount_diff_names_fail(self):
        pet_name = "Rat-CottonCandyBlue"
        mount_name = "Sloth-Red"
        with pytest.raises(InvalidPetMountPair) as exec_info:
            PetMountPair(pet=Pet(pet_name),
                         mount=Mount(mount_name, availability_status=None))

        err_mesg = str(exec_info.value)
        assert err_mesg.startswith(f"pet name '{pet_name}' must equal mount name '{mount_name}'")
        assert exec_info.errisinstance(ClickException)
        assert exec_info.errisinstance(YouFoundABugRewardError)
        assert exec_info.value.exit_code == 1

    @pytest.mark.parametrize("pair", unfeedable_pairs)
    def test_can_feed_pet_false(self, pair: PetMountPair):
        assert pair.can_feed_pet() is False

    @pytest.mark.parametrize("pair", feedable_pairs)
    def test_can_feed_pet_true(self, pair: PetMountPair):
        assert pair.can_feed_pet() is True

    # if pet is feedable, there cannot be a mount
    @pytest.mark.parametrize("pair", [empty_pair] + feedable_pairs)
    def test_mount_available_false(self, pair: PetMountPair):
        assert pair.mount_available() is False

    @pytest.mark.parametrize("pair", mount_available_pairs)
    def test_mount_available_true(self, pair: PetMountPair):
        assert pair.mount_available() is True

    @pytest.mark.parametrize("pair", [phoenix_pet_only_pair] + feedable_pairs)
    def test_pet_available_true(self, pair):
        assert pair.pet_available() is True

    @pytest.mark.parametrize("pair", [empty_pair, phoenix_mount_only_pair])
    def test_pet_available_false(self, pair):
        assert pair.pet_available() is False
