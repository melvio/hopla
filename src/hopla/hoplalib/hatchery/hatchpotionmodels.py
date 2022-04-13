#!/usr/bin/env python3
"""
Module with models for hatching potions.
"""
from dataclasses import dataclass, field
from typing import Dict, Iterator

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.hatchpotion_data import HatchPotionData


class HatchPotionException(YouFoundABugRewardError):
    """Exception raised when there is an error with an hatching potion."""


@dataclass
class HatchPotion:
    """A habitica hatching potion."""
    name: str
    quantity: int = 1

    def __post_init__(self):
        if self.name not in HatchPotionData.hatch_potion_names:
            raise HatchPotionException(f"{self.name} is not a valid hatching potion name.")
        if self.quantity < 0:
            raise HatchPotionException(f"{self.quantity} is below 0.")

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

    potions: Dict[str, int] = field(init=True, compare=False, default_factory=dict)
    __potions: Dict[str, HatchPotion] = field(init=False)

    def __post_init__(self):
        """Use the given potions to create __potions."""
        self.__potions: Dict[str, HatchPotion] = {
            name: HatchPotion(name, quantity=quantity)
            for (name, quantity) in self.potions.items()
        }

    def __len__(self) -> int:
        return len(self.__potions)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__potions)

    def __getitem__(self, name: str) -> HatchPotion:
        return self.__potions[name]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__potions=})"

    def values(self) -> Iterator[HatchPotion]:
        """Like dict.values but for an HatchPotionCollection."""
        for potion in self.__potions.values():
            yield potion

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
