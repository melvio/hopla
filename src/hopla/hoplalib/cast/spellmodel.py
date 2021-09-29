#!/usr/bin/env python3
"""
Module with spell models and data.
"""
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from hopla.hoplalib.errors import YouFoundABugRewardError


class SpellData:
    """A class with data about spells.

    @see: habitica api content | jq. spells
    """

    warrior_spells_single_arg = ["defensiveStance", "valorousPresence", "intimidate"]
    mage_spells_single_arg = ["mpheal", "earth"]
    rogue_spells_single_arg = ["toolsOfTrade", "stealth"]
    healer_spells_single_arg = ["heal", "brightness", "protectAura", "healAll"]

    single_arg_spells: List[str] = (
            warrior_spells_single_arg
            + mage_spells_single_arg
            + rogue_spells_single_arg
            + healer_spells_single_arg
    )


@dataclass
class Spell:
    """A spell."""

    def __init__(self, spell_name: str,
                 *, target_id: UUID = None):
        if spell_name not in SpellData.single_arg_spells:
            raise YouFoundABugRewardError(f"{spell_name=} does not exist.")
        self.spell_name = spell_name
        self.target_id: Optional[UUID] = target_id
        """ not supported now """

    @property
    def class_name(self) -> str:
        """Get the Habitica class from the spell name.

        see: https://habitica.fandom.com/wiki/Class_System
        """
        if self.spell_name in SpellData.warrior_spells_single_arg:
            return "warrior"
        if self.spell_name in SpellData.mage_spells_single_arg:
            return "mage"
        if self.spell_name in SpellData.healer_spells_single_arg:
            return "healer"
        if self.spell_name in SpellData.rogue_spells_single_arg:
            return "rogue"

        raise YouFoundABugRewardError(f"{self.spell_name=} not implemented yet")
        # Mage: fireball="Burst of Flames", mpheal="Ethereal Surge", earth="Earthquake",
        #         frost="Chilling Frost"
        # Warrior: smash="Brutal Smash", defensiveStance="Defensive Stance",
        #          valorousPresence="Valorous Presence", intimidate="Intimidating Gaze"

        # Rogue: pickPocket="Pickpocket", backStab="Backstab", toolsOfTrade="Tools of the Trade",
        # stealth="Stealth"

        # Healer: heal="Healing Light", protectAura="Protective Aura",
        #          brightness="Searing Brightness",
        #         healAll="Blessing"
        # Transformation Items: snowball="Snowball", spookySparkles="Spooky Sparkles",
        #                       seafoam="Seafoam", shinySeed="Shiny Seed"
