#!/usr/bin/env python3
"""
Module with algorithms for hatching many eggs.
"""
from dataclasses import dataclass, field
from typing import Any, List

from hopla.hoplalib.hatchery.eggmodels import Egg, EggCollection, EggException
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchPotion, \
    HatchPotionCollection
from hopla.hoplalib.zoo.petmodels import Pet


@dataclass(frozen=True)
class HatchPlanItem:
    """Plan to hatch a specific egg with a specified potion."""
    egg: Egg
    potion: HatchPotion

    def __post_init__(self):
        if self.egg.can_be_hatched_by(potion=self.potion) is False:
            msg = f"Cannot hatch {self.egg.name} with {self.potion.name} potion"
            raise EggException(msg)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, HatchPlanItem) is False:
            return False
        # We don't care about quantity here. We always use 1 egg and 1 potion
        # for any hatching in our hatch plan.
        return other.egg.name == self.egg.name and other.potion.name == self.potion.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.egg.name}: {self.potion.name})"

    def result_pet_name(self) -> str:
        """
        Return the pet name that comes from hatching the egg with the given potion.
        """
        return f"{self.egg.name}-{self.potion.name}"

    def format_item(self) -> str:
        """Terminal-printable representation of this HatchPlanItem."""
        return (
            f"A {self.egg.name} egg will be hatched by a {self.potion.name} potion.\n"
        )

    def can_hatch_with_pet(self, pet: Pet) -> bool:
        """
        Return True if we can hatch this item without clashing with the given pet.
        If the hatching would clash, return False

        :param pet: The pet to check against.
        :return: True if we can safely hatch if we only had this pet.
        """
        return (pet.is_available() is False) or (pet.name != self.result_pet_name())

    def can_hatch_with_pets(self, pets: List[Pet]) -> bool:
        """
        Return True if we can hatch this item without clashing with the given pets.
        If any of the hatchings would clash, return False

        :param pets: The pets to check against.
        :return: True if we can safely hatch even if we had all these pets.
        """
        return all(self.can_hatch_with_pet(pet) for pet in pets)


@dataclass
class HatchPlan:
    """Plan to hatch a specific eggs with specified potions."""

    plan: List[HatchPlanItem] = field(init=False, default_factory=list)

    def __iter__(self):
        return iter(self.plan)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.plan if len(self.plan) > 0 else 'empty'})"

    def __len__(self) -> int:
        return len(self.plan)

    def is_empty(self) -> bool:
        """Return true if there no items in the hatch plan."""
        return len(self.plan) == 0

    def format_plan(self) -> str:
        """Terminal-printable representation of this HatchPlan."""
        return "".join([item.format_item() for item in self.plan])

    def add(self, *, egg: Egg, potion: HatchPotion) -> "HatchPlan":
        """Make the plan to hatch the egg with the specified potion.

        :param egg:
        :param potion:
        :return: self for chaining
        """
        hatch_plan_item = HatchPlanItem(egg=egg, potion=potion)
        self.plan.append(hatch_plan_item)
        return self

    def remove_hatch_item_if_pet_available(self, pets: List[Pet]) -> "HatchPlan":
        """Remove the hatching plan items for pets that are available.

        :param pets: list of pets to check for clashes with the hatching
        :return: self for chaining
        """
        pet_names: List[str] = [pet.name for pet in pets if pet.is_available()]

        self.plan = [hatch_item for hatch_item in self.plan
                     if hatch_item.result_pet_name() not in pet_names]

        return self


@dataclass
class HatchPlanMaker:
    """
    Object that takes a collection of eggs and hatching potions and
    return a plan to hatch the eggs.
    """

    def __init__(self, *,
                 egg_collection: EggCollection,
                 hatch_potion_collection: HatchPotionCollection,
                 pets: List[Pet]):
        self.__eggs = egg_collection
        self.__potions = hatch_potion_collection
        self.__pets = pets
        self.__hatch_plan = HatchPlan()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(\n"
            f"    {self.__eggs},\n"
            f"    {self.__potions},\n"
            f"    plan={self.__hatch_plan}\n"
            ")"
        )

    def make_plan(self) -> HatchPlan:
        """Given an collection of eggs and hatching potions, make a plan to hatch the eggs."""
        for egg in self.__eggs.values():
            for potion in self.__potions.values():
                can_hatch: bool = (
                        egg.can_be_hatched_by(potion)
                        and HatchPlanItem(egg, potion).can_hatch_with_pets(self.__pets)
                )
                if can_hatch:
                    self.__hatch_plan.add(egg=egg, potion=potion)
                    self.__eggs.remove_egg(egg)
                    self.__potions.remove_hatch_potion(potion)

        return self.__hatch_plan
