#!/usr/bin/env python3
import random

import pytest

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.zoo.fooddata import FoodData
from hopla.hoplalib.zoo.foodmodels import FeedingStatus, InvalidFeedingStatus
from hopla.hoplalib.zoo.petdata import PetData
from hopla.hoplalib.zoo.petmodels import InvalidPet, \
    Pet, PetMountPair, Zoo, ZooBuilder, ZooHelper
from tests.testutils.user_test_utils import UserTestUtil

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

    def test___repr__(self):
        pet_name = "Fox-Shadow"
        feeding_status = FeedingStatus(10)
        pet = Pet(pet_name, feeding_status=feeding_status)

        result = str(pet)

        expected = f"Pet(self.pet_name='{pet_name}', self.feeding_status={feeding_status})"
        assert result == expected

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

    @pytest.mark.parametrize(
        "pet,food_name,expected_times", [
            (Pet("Hedgehog-Shade", feeding_status=FeedingStatus(10)), "Chocolate", 8),
            (Pet("Hedgehog-Shade", feeding_status=FeedingStatus(10)), "Milk", 20),
            (Pet("Egg-Base"), "Meat", 9),
            (Pet("Egg-Zombie"), "CottonCandyPink", 23),
            (Pet("Egg-Base", feeding_status=FeedingStatus(40)), "Meat", 2),
            (Pet("Egg-Base", feeding_status=FeedingStatus(44)), "Meat", 2),
            (Pet("Egg-Golden", feeding_status=FeedingStatus(47)), "Fish", 2),
        ]
    )
    def test_required_food_items_until_mount(self, pet: Pet,
                                             food_name: str,
                                             expected_times: int):
        times_result: int = pet.required_food_items_until_mount(food_name)

        assert times_result == expected_times


class TestPetMountPair:
    def test_feed_status_fail(self):
        pet = Pet("LionCub-Watery", feeding_status=None)

        with pytest.raises(InvalidFeedingStatus) as execinfo:
            PetMountPair(pet,
                         pet_available=True,
                         mount_available=False)

        err_msg = str(execinfo.value)
        assert f"PetMountPair requires that pet={pet} has a feeding status" in err_msg

    def test___repr__(self):
        feed_status = FeedingStatus(20)
        pet = Pet("Monkey-Skeleton", feeding_status=feed_status)
        pet_available = True
        mount_available = True

        pair = PetMountPair(pet,
                            pet_available=pet_available,
                            mount_available=mount_available)
        result = str(pair)

        expected = ("PetMountPair({"
                    "'pet': Pet(self.pet_name='Monkey-Skeleton', "
                    "self.feeding_status=FeedingStatus(20)), "
                    "'pet_available': True, ""'mount_available': True})")
        assert result == expected

    def test_can_feed_pet_mount_available(self):
        # pet itself is feedable, but mount is available,
        # so cant feed pet should return False
        pet = Pet("Wolf-Base", feeding_status=FeedingStatus(5))
        pair = PetMountPair(pet, pet_available=True, mount_available=True)

        result = pair.can_feed_pet()

        assert result is False

    def test_can_feed_pet_pet_unavailable(self):
        # pet itself is feedable, but pet is unavailable,
        # so cant feed pet should return False
        pet = Pet("Dragon-SolarSystem", feeding_status=FeedingStatus(-1))
        pair = PetMountPair(pet, pet_available=False, mount_available=True)

        result = pair.can_feed_pet()

        assert result is False

    @pytest.mark.parametrize(
        "unfeedable_pet_name",
        random.sample(PetData.unfeedable_pet_names, k=15)
        # Remark: The data is not entirely realistic, this includes some
        # mount-only animals too. However, they should also
        # return False when can_feed_pet is called.
    )
    def test_can_feed_pet_pet_is_unfeedable(self, unfeedable_pet_name: str):
        # pet itself is not feedable, so cant feed pet should return False
        pet = Pet(unfeedable_pet_name, feeding_status=FeedingStatus(-1))
        pair = PetMountPair(pet, pet_available=True, mount_available=False)

        result = pair.can_feed_pet()

        assert result is False


class TestZooBuilder:
    def test__init__(self):
        animal_name = "Wolf-Zombie"
        feeding_status = 5
        animal_name2 = "Deer-Base"
        feeding_status2 = 10

        pets_dict = {animal_name: feeding_status, animal_name2: feeding_status2}
        mounts_dict = {animal_name: True}
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets_dict, mounts=mounts_dict)

        builder = ZooBuilder(user)

        assert builder.pets == pets_dict
        assert builder.mounts == mounts_dict

    def test__repr__(self):
        animal_name = "Wolf-CottonCandyBlue"
        feeding_status = 5
        pets_dict = {animal_name: feeding_status}
        mounts_dict = {animal_name: True}
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets_dict, mounts=mounts_dict)

        builder_str = str(ZooBuilder(user))

        assert "'pets': " + str(pets_dict) in builder_str
        assert "'mounts': " + str(mounts_dict) in builder_str

    def test_build_empty_zoo(self):
        empty_zoo = {"pets": {}, "mounts": {}}
        user = HabiticaUser({"items": empty_zoo})

        zoo: Zoo = ZooBuilder(user).build()

        assert zoo == {}

    def test_build_raised_pet(self):
        animal_name = "BearCub-Shadow"
        feed_status = -1  # i.e. No pet, just mount
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets={animal_name: feed_status},
                                                        mounts={animal_name: True})

        zoo: Zoo = ZooBuilder(user).build()

        assert len(zoo) == 1

        result_pair = zoo[animal_name]
        assert result_pair.pet.pet_name == animal_name
        assert result_pair.pet.feeding_status == FeedingStatus(feed_status)
        assert result_pair.mount_available
        assert result_pair.pet_available is False

    def test_build_no_pet_yes_mount(self):
        animal_name = "Aether-Invisible"
        user: HabiticaUser = UserTestUtil.user_with_zoo(mounts={animal_name: True})

        zoo: Zoo = ZooBuilder(user).build()

        assert len(zoo) == 1
        result_pair = zoo[animal_name]
        assert result_pair.pet.pet_name == animal_name
        assert result_pair.mount_available
        assert result_pair.pet_available is False

    def test_build_yes_pet_no_mount(self):
        animal_name = "Dragon-Skeleton"
        feeding_status = 27
        user = UserTestUtil.user_with_zoo(pets={animal_name: feeding_status})

        zoo: Zoo = ZooBuilder(user).build()

        assert len(zoo) == 1
        result_pair = zoo[animal_name]
        assert result_pair.pet.pet_name == animal_name
        assert result_pair.pet.feeding_status == FeedingStatus(feeding_status)
        assert result_pair.mount_available is False
        assert result_pair.pet_available


class TestZooHelper:
    def test_filter_on_pet_mount_pair(self):
        pets = {"Owl-Golden": -1, "Ferret-Red": 27, "Phoenix-Base": 5, "Parrot-Base": 10}
        mounts = {"BearCub-Desert": True}
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets, mounts=mounts)
        zoo: Zoo = ZooBuilder(user).build()

        def predicate(pair: PetMountPair) -> bool:
            # arbitrary filter function
            return (pair.pet.pet_name == "Parrot-Base"
                    or pair.mount_available
                    or int(pair.pet.feeding_status) == 27)

        helper = ZooHelper(zoo)
        filtered_zoo: Zoo = helper.filter_on_pet_mount_pairs(predicate=predicate)

        expected_pets = sorted(["Ferret-Red", "Parrot-Base", "BearCub-Desert"])
        assert all(expected_pet in filtered_zoo.keys() for expected_pet in expected_pets)

    def test_get_feedable_zoo(self):
        pets = {
            "BearCub-Desert": 5,  # we have the mount, not hungry
            "Owl-Golden": -1,  # we don't have the pet
            "Ferret-Red": 27,  # can be fed
            "Phoenix-Base": 5,  # unfeedable pet
            "Parrot-Base": 10,  # can be fed
        }
        mounts: dict = {"BearCub-Desert": True}
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets, mounts=mounts)
        zoo: Zoo = ZooBuilder(user).build()

        helper = ZooHelper(zoo)
        filtered_zoo: Zoo = helper.get_feedable_zoo()

        expected_pets = ["Ferret-Red", "Parrot-Base"]
        assert all(expected_pet in filtered_zoo.keys() for expected_pet in expected_pets)

    def test_filter_on_pet_name(self):
        pets = {
            "BearCub-Desert": 5, "Owl-Golden": -1, "Ferret-Red": 27,
            "Phoenix-Base": 5, "Parrot-Base": 10
        }
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets)
        zoo: Zoo = ZooBuilder(user).build()

        helper = ZooHelper(zoo)
        filtered_zoo: Zoo = helper.filter_on_pet_name(lambda name: name.endswith("-Base"))

        expected_pets = ["Phoenix-Base", "Parrot-Base"]
        assert all(expected_pet in filtered_zoo.keys() for expected_pet in expected_pets)

    def test_filter_on_pet(self):
        pets: dict = {"BearCub-Desert": 9, "Owl-Golden": -1, "Ferret-Red": 27, "Phoenix-Base": 5,
                      "Parrot-Base": 10}
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets)
        zoo: Zoo = ZooBuilder(user).build()

        def predicate(pet: Pet) -> bool:
            return int(pet.feeding_status) < 9

        helper = ZooHelper(zoo)
        filtered_zoo: Zoo = helper.filter_on_pet(predicate=predicate)

        expected_pets = ["Owl-Golden", "Phoenix-Base"]
        assert all(expected_pet in filtered_zoo.keys() for expected_pet in expected_pets)
