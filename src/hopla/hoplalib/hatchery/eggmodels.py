#!/usr/bin/env python3
"""
Module with models for eggs.
"""
from dataclasses import dataclass
from typing import Dict

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.hatchdata import EggData
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchingPotion


class EggException(YouFoundABugRewardError):
    """Exception raised when there is an error with an Egg."""


@dataclass
class Egg:
    """An Habitica egg."""

    def __init__(self, name: str, *, quantity: int = 1):
        if name not in EggData.egg_names:
            raise EggException(f"{name} is not a valid egg name.")
        if quantity < 0:
            raise EggException(f"{quantity} is below 0.")

        self.name = name
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}: {self.quantity})"

    def is_standard_egg(self) -> bool:
        """Return True if this is a drop egg. Else False"""
        return self.name in EggData.drop_egg_names

    def is_quest_egg(self) -> bool:
        """Return True if this is a quest egg. Else False"""
        return self.name in EggData.quest_egg_names

    def can_be_hatched_by(self, potion: HatchingPotion) -> bool:
        """Return true if the specified potion can hatch this egg."""
        if self.is_quest_egg():
            return potion.is_standard_hatching_potion()
        return True


@dataclass
class EggCollection:
    """Collection of eggs backed by a Dict[str, Egg].

    This data structure guarantees that the eggs in the collection have at least
    a quantity that is larger than 0. When the all the eggs of a certain type
    are removed, then egg will be removed from the collection in its entirely.
    """

    def __init__(self, eggs: Dict[str, int]):
        self.__eggs: Dict[str, Egg] = {
            name: Egg(name, quantity=quantity) for (name, quantity) in eggs.items()
            if quantity > 0
        }

    def __iter__(self):
        return iter(self.__eggs)

    def __getitem__(self, name: str) -> Egg:
        return self.__eggs[name]

    def remove_egg(self, egg: Egg) -> "EggCollection":
        """Remove a single eggs from the EggCollection.

        :param egg: egg to remove
        :return: The updated EggCollection
        """
        if self.__eggs.get(egg.name) is None:
            raise EggException(f"{egg.name} was not in the collection {self.__eggs}")

        self.__eggs[egg.name].quantity -= 1
        if self.__eggs[egg.name].quantity == 0:
            del self.__eggs[egg.name]

        return self

    def get_standard_egg_collection(self) -> "EggCollection":
        """Return all the standard eggs in this collection."""
        return EggCollection({
            name: egg.quantity for (name, egg) in self.__eggs.items() if egg.is_standard_egg()
        })

    def get_quest_egg_collection(self) -> "EggCollection":
        """Return all the quest eggs in this collection."""
        return EggCollection({
            name: egg.quantity for (name, egg) in self.__eggs.items() if egg.is_quest_egg()
        })
