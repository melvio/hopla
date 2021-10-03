#!/usr/bin/env python3
from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.zoo.foodmodels import FeedStatus
from hopla.hoplalib.zoo.petmodels import Pet, PetMountPair
from hopla.hoplalib.zoo.zoomodels import Zoo, ZooBuilder, ZooHelper
from tests.testutils.user_test_utils import UserTestUtil


class TestZooBuilder:
    def test__init__(self):
        animal_name, feed_status = "Wolf-Zombie", 5
        animal_name2, feed_status2 = "Deer-Base", 10

        pets_dict = {animal_name: feed_status, animal_name2: feed_status2}
        mounts_dict = {animal_name: True}
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets_dict, mounts=mounts_dict)

        builder = ZooBuilder(user)

        assert builder.pets == pets_dict
        assert builder.mounts == mounts_dict

    def test__repr__(self):
        animal_name, feed_status = "Wolf-CottonCandyBlue", 5
        pets_dict = {animal_name: feed_status}
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

    def test_build_released_zoo(self):
        pass

    def test_build_raised_pets(self):
        animal_name = "BearCub-Shadow"
        feed_status = -1  # i.e. No pet, just mount
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets={animal_name: feed_status},
                                                        mounts={animal_name: True})

        result_zoo: Zoo = ZooBuilder(user).build()

        assert len(result_zoo) == 1

        result_pair: PetMountPair = result_zoo[animal_name]
        assert result_pair.pet.name == animal_name
        assert result_pair.pet.feed_status == FeedStatus(feed_status)
        assert result_pair.mount_available()
        assert result_pair.pet_available() is False

    def test_build_no_pet_yes_mount(self):
        animal_name = "Aether-Invisible"
        user: HabiticaUser = UserTestUtil.user_with_zoo(mounts={animal_name: True})

        zoo: Zoo = ZooBuilder(user).build()

        assert len(zoo) == 1
        result_pair: PetMountPair = zoo[animal_name]
        assert result_pair.pet is None
        assert result_pair.mount_available()
        assert result_pair.pet_available() is False

    def test_build_yes_pet_no_mount(self):
        animal_name = "Dragon-Skeleton"
        feed_status = 27
        user = UserTestUtil.user_with_zoo(pets={animal_name: feed_status})

        zoo: Zoo = ZooBuilder(user).build()

        assert len(zoo) == 1
        result_pair: PetMountPair = zoo[animal_name]
        assert result_pair.pet.name == animal_name
        assert result_pair.pet.feed_status == FeedStatus(feed_status)
        assert result_pair.mount_available() is False
        assert result_pair.pet_available()


class TestZooHelper:
    def test_filter_on_pet_mount_pair(self):
        pets = {"Owl-Golden": -1, "Ferret-Red": 27, "Phoenix-Base": 5, "Parrot-Base": 10}
        mounts = {"BearCub-Desert": True}
        user: HabiticaUser = UserTestUtil.user_with_zoo(pets=pets, mounts=mounts)
        zoo: Zoo = ZooBuilder(user).build()

        def predicate(pair: PetMountPair) -> bool:
            # arbitrary filter function
            return pair.pet is not None and (
                    pair.pet.name == "Parrot-Base"
                    or pair.mount_available()
                    or int(pair.pet.feed_status) == 27
            )

        helper = ZooHelper(zoo)
        filtered_zoo: Zoo = helper.filter_on_pet_mount_pairs(predicate=predicate)

        expected_pets = sorted(["Ferret-Red", "Parrot-Base"])
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
            return int(pet.feed_status) < 9

        helper = ZooHelper(zoo)
        filtered_zoo: Zoo = helper.filter_on_pet(predicate=predicate)

        expected_pets = ["Owl-Golden", "Phoenix-Base"]
        assert all(expected_pet in filtered_zoo.keys() for expected_pet in expected_pets)
