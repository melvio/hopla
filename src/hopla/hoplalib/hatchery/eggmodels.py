#!/usr/bin/env python3
"""
Module with models for eggs.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.egg_data import EggData
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchPotion


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

    def __eq__(self, other: Any) -> bool:
        """Return True if both eggs have the same name and same quantity."""
        if isinstance(other, Egg) is False:
            return False
        return self.name == other.name and self.quantity == other.quantity

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}: {self.quantity})"

    def is_standard_egg(self) -> bool:
        """Return True if this is a drop egg. Else False"""
        return self.name in EggData.drop_egg_names

    def is_quest_egg(self) -> bool:
        """Return True if this is a quest egg. Else False"""
        return self.name in EggData.quest_egg_names

    def can_be_hatched_by(self, potion: HatchPotion) -> bool:
        """Return true if the specified potion can hatch this egg."""
        if potion.quantity == 0 or self.quantity == 0:
            return False
        if self.is_quest_egg():
            return potion.is_standard_hatch_potion()
        return True


@dataclass
class EggCollection:
    """Collection of eggs, backed by a Dict[str, Egg]."""

    eggs: Dict[str, int] = field(init=True, compare=False, default_factory=dict)
    __eggs: Dict[str, Egg] = field(init=False)

    def __post_init__(self):
        """Use the given eggs to create __eggs."""
        self.__eggs: Dict[str, Egg] = {
            name: Egg(name, quantity=quantity) for (name, quantity) in self.eggs.items()
        }

    def __len__(self) -> int:
        return len(self.__eggs)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__eggs)

    def __getitem__(self, name: str) -> Egg:
        return self.__eggs[name]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__eggs=})"

    def values(self) -> Iterator[Egg]:
        """Like dict.values but for an EggCollection."""
        for egg in self.__eggs.values():
            yield egg

    def remove_egg(self, egg: Egg) -> "EggCollection":
        """Remove a single eggs from the EggCollection.

        :param egg: egg to remove
        :return: The updated EggCollection
        """
        if self.__eggs.get(egg.name) is None:
            raise EggException(f"{egg.name} was not in the collection {self.__eggs}")
        if self.__eggs[egg.name].quantity == 0:
            raise EggException(f"We had 0 {egg.name} in the collection. Cannot remove any more.")

        self.__eggs[egg.name].quantity -= 1

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
