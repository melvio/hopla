#!/usr/bin/env python3
"""
Module with models for hatching potions.
"""
from dataclasses import dataclass
from typing import Dict

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.hatchdata import HatchingPotionData


class HatchingPotionException(YouFoundABugRewardError):
    """Exception raised when there is an error with an hatching potion."""


@dataclass
class HatchingPotion:
    """A habitica hatching potion."""

    def __init__(self, name: str, *, quantity: int = 1):
        if name not in HatchingPotionData.hatching_potion_names:
            raise HatchingPotionException(f"{name} is not a valid hatching potion name.")
        if quantity < 0:
            raise HatchingPotionException(f"{quantity} is below 0.")

        self.name = name
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}: {self.quantity})"

    def is_standard_hatching_potion(self) -> bool:
        """Return true if this is a standard hatching potion."""
        return self.name in HatchingPotionData.drop_hatching_potion_names

    def is_magic_hatching_potion(self) -> bool:
        """Return true if this is a magic hatching potion."""
        return self.name in HatchingPotionData.magic_hatching_potion_names

    def is_wacky_hatching_potion(self) -> bool:
        """Return true if this is a wacky hatching potion."""
        return self.name in HatchingPotionData.wacky_hatching_potion_names


@dataclass
class HatchingPotionCollection:
    """A collection of hatching potions backed by a Dict[str, Egg].

    This data structure guarantees that the potion in the collection have at least
    a quantity that is larger than 0. When the all the potions of a certain type
    are removed, then the potion will be removed from the collection in its entirely.
    """

    def __init__(self, potions: Dict[str, int]):
        self.__potions: Dict[str, HatchingPotion] = {
            name: HatchingPotion(name, quantity=quantity) for (name, quantity) in potions.items()
            if quantity > 0
        }

    def __iter__(self):
        return iter(self.__potions)

    def __getitem__(self, name: str) -> HatchingPotion:
        return self.__potions[name]

    def remove_hatching_potion(self, potion: HatchingPotion) -> "HatchingPotionCollection":
        """Remove a single hatching potion from this collection.

        :param potion: The potion to remove.
        :return: The updated HatchingPotionCollection
        """
        if self.__potions.get(potion.name) is None:
            raise HatchingPotionException(
                f"{potion.name} was not in the collection {self.__potions}"
            )
        self.__potions[potion.name].quantity -= 1
        if self.__potions[potion.name].quantity == 0:
            del self.__potions[potion.name]

        return self
