#!/usr/bin/env python3
"""
Module with algorithms for hatching many eggs.
"""
from dataclasses import dataclass
from typing import Any, List

from hopla.hoplalib.hatchery.eggmodels import Egg, EggCollection
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchingPotion, \
    HatchingPotionCollection
from hopla.hoplalib.zoo.petmodels import Pet


@dataclass(frozen=True)
class HatchPlanItem:
    """Plan to hatch a specific egg with a specified potion."""
    egg: Egg
    potion: HatchingPotion

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
            f"The '{self.egg.name}' egg will be hatched by the '{self.potion.name}' potion."
        )


@dataclass
class HatchPlan:
    """Plan to hatch a specific eggs with specified potions."""

    def __init__(self):
        self.plan: List[HatchPlanItem] = []

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, HatchPlan) is False:
            return False
        return self.plan == other.plan

    def __len__(self) -> int:
        return len(self.plan)

    def __iter__(self):
        return iter(self.plan)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.plan if len(self.plan) > 0 else 'empty'})"

    def add(self, *, egg: Egg, potion: HatchingPotion) -> "HatchPlan":
        """Make the plan to hatch the egg with the specified potion.

        :param egg:
        :param potion:
        :return: self for chaining
        """
        hatch_plan_item = HatchPlanItem(egg=egg, potion=potion)
        self.plan.append(hatch_plan_item)
        return self

    def remove_hatch_if_pets_available(self, pets: List[Pet]) -> "HatchPlan":
        """Remove the hatching plan items for pets that are available.

        :param pets: list of pets to check for clashes with the hatching
        :return: self for chaining
        """
        pet_names: List[str] = [pet.pet_name for pet in pets
                                if pet.is_available()]

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
                 hatch_potion_collection: HatchingPotionCollection):
        self.__eggs = egg_collection
        self.__potions = hatch_potion_collection
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
        for egg_name in self.__eggs:
            egg: Egg = self.__eggs[egg_name]
            for potion_name in self.__potions:
                potion: HatchingPotion = self.__potions[potion_name]
                if egg.can_be_hatched_by(potion):
                    self.__hatch_plan.add(egg=egg, potion=potion)
                    self.__eggs.remove_egg(egg)
                    self.__potions.remove_hatching_potion(potion)

        return self.__hatch_plan
