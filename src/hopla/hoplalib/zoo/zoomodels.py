#!/usr/bin/env python3
"""
Module with models for collections of pets and mounts.
"""
from typing import Callable, Dict
from dataclasses import dataclass

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.zoo.foodmodels import FeedStatus
from hopla.hoplalib.zoo.petmodels import Mount, Pet, PetMountPair

Zoo = Dict[str, PetMountPair]
"""
Zoo is dictionary with key pet name keys for O(1) access to the
PetMountPair.
"""


@dataclass(frozen=True)
class ZooHelper:
    """Class with helper functions for a Zoo."""
    zoo: Zoo

    def filter_on_pet_mount_pairs(self, predicate: Callable[[PetMountPair], bool]) -> Zoo:
        """Filter the zoo on the pair. This does not change the underlying zoo.

        :param predicate: Include the PetMountPair if the predicate returns True, else
                          omit the pair.
        :return: A filtered Zoo
        """
        return {
            pet_name: pair for (pet_name, pair) in self.zoo.items() if predicate(pair)
        }

    def get_feedable_zoo(self) -> Zoo:
        """Helper function to get only the pets that can be fed in this Zoo."""
        return self.filter_on_pet_mount_pairs(PetMountPair.can_feed_pet)

    def filter_on_pet_name(self, predicate: Callable[[str], bool]) -> Zoo:
        """Filter the zoo on the pet name. This does not change the underlying zoo.

        :param predicate: Include the PetMountPair if the predicate returns True, else
                          omit the pair.
        :return: A filtered zoo.
        """
        return {
            pet_name: pair for (pet_name, pair) in self.zoo.items() if predicate(pet_name)
        }

    def filter_on_pet(self, predicate: Callable[[Pet], bool]) -> Zoo:
        """Filter the zoo on the pet object. This does not change the underlying zoo.

        :param predicate: Include the PetMountPair if the predicate returns True, else
                          omit the pair.
        :return: A filtered zoo.
        """
        return {
            pet_name: pair for (pet_name, pair) in self.zoo.items() if predicate(pair.pet)
        }


class ZooBuilder:
    """
    Class that creates a Zoo from a HabiticaUser using the
    builder design pattern.
    """

    def __init__(self, user: HabiticaUser):
        self.pets: dict = user.get_pets()
        self.mounts: dict = user.get_mounts()
        self.__zoo: Zoo = {}  # empty until build() is called

    def __repr__(self):
        return self.__class__.__name__ + f"({self.__dict__})"

    def build(self) -> Zoo:
        """Create the Zoo. Return the Zoo in case of success"""

        # loop through the pets
        for pet_name, feed_status in self.pets.items():
            pet = Pet(pet_name, feed_status=FeedStatus(feed_status))

            if self.mounts.get(pet_name) is not None:
                mount = Mount(
                    mount_name=pet_name,
                    availability_status=self.mounts[pet_name]
                )
                del self.mounts[pet_name]  # no need to handle the mount twice
            else:
                mount = None
            self.__zoo[pet_name] = PetMountPair(pet=pet, mount=mount)

        # loop through the remaining mounts
        for mount_name, availability_status in self.mounts.items():
            if mount_name not in self.pets:
                # We found a mount without a pet. This is possible for rares.
                mount = Mount(mount_name, availability_status=availability_status)
                self.__zoo[mount_name] = PetMountPair(pet=None, mount=mount)

        return self.__zoo
