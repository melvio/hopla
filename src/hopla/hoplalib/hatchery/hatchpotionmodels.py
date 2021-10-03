#!/usr/bin/env python3
"""
Module with models for hatching potions.
"""
from dataclasses import dataclass
from typing import Dict

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.hatchdata import HatchPotionData


class HatchPotionException(YouFoundABugRewardError):
    """Exception raised when there is an error with an hatching potion."""


@dataclass
class HatchPotion:
    """A habitica hatching potion."""

    def __init__(self, name: str, *, quantity: int = 1):
        if name not in HatchPotionData.hatch_potion_names:
            raise HatchPotionException(f"{name} is not a valid hatching potion name.")
        if quantity < 0:
            raise HatchPotionException(f"{quantity} is below 0.")

        self.name = name
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}: {self.quantity})"

    def is_standard_hatch_potion(self) -> bool:
        """Return true if this is a standard hatching potion."""
        return self.name in HatchPotionData.drop_hatch_potion_names

    def is_magic_hatch_potion(self) -> bool:
        """Return true if this is a magic hatching potion."""
        return self.name in HatchPotionData.magic_hatch_potion_names

    def is_wacky_hatch_potion(self) -> bool:
        """Return true if this is a wacky hatching potion."""
        return self.name in HatchPotionData.wacky_hatch_potion_names


@dataclass
class HatchPotionCollection:
    """A collection of hatching potions, backed by a Dict[str, Egg]."""

    def __init__(self, potions: Dict[str, int] = None):
        if potions is None:
            potions = {}
        self.__potions: Dict[str, HatchPotion] = {
            name: HatchPotion(name, quantity=quantity) for (name, quantity) in potions.items()
        }

    def __len__(self) -> int:
        return len(self.__potions)

    def __iter__(self):
        return iter(self.__potions)

    def __getitem__(self, name: str) -> HatchPotion:
        return self.__potions[name]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__potions=})"

    def remove_hatch_potion(self, potion: HatchPotion) -> "HatchPotionCollection":
        """Remove a single hatching potion from this collection.

        :param potion: The potion to remove.
        :return: The updated HatchPotionCollection
        """
        if self.__potions.get(potion.name) is None:
            raise HatchPotionException(
                f"{potion.name} was not in the collection {self.__potions}"
            )
        if self.__potions.get(potion.name).quantity == 0:
            raise HatchPotionException(
                f"We had 0 {potion.name} in the collection. Cannot remove any more."
            )

        self.__potions[potion.name].quantity -= 1
        return self
