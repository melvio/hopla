#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla cast` command.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

import click
import requests

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.requests_helper import get_data_or_exit

log = logging.getLogger()


class SpellData:
    """A class with data about spells.

    @see: habitica api content | jq. spells
    """

    warrior_spells_single_arg = ["defensiveStance", "valorousPresence", "intimidate"]
    mage_spells_single_arg = ["mpheal", "earth"]
    rogue_spells_single_arg = ["toolsOfTrade", "stealth"]
    healer_spells_single_arg = ["heal", "brightness", "protectAura", "healAll"]

    single_arg_spell_choices: List[str] = (
            warrior_spells_single_arg
            + mage_spells_single_arg
            + rogue_spells_single_arg
            + healer_spells_single_arg
    )


@dataclass
class Spell:
    """A spell."""
    spell_name: str
    target_id: Optional[UUID] = None
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


@dataclass
class PostCastRequest(HabiticaRequest):
    """HabiticaRequester that POSTs to the spell cast endpoint.

    [APIDOCS](https://habitica.com/apidoc/#api-User-UserCast)
    """
    spell: Spell

    @property
    def url(self) -> str:
        """Get the url"""
        path_extension = f"/user/class/cast/{self.spell.spell_name}"
        return UrlBuilder(path_extension=path_extension).url

    def post_spell(self) -> requests.Response:
        """Perform the user get request and return the response"""
        return requests.post(url=self.url, headers=self.default_headers)


@click.command()
@click.argument("spell_name", type=click.Choice(SpellData.single_arg_spell_choices))
def cast(spell_name):
    """Cast a spell.

    SPELL_NAME the name of the spell to cast

    Currently, there is only support for spells that are not cast on one
    single task.

    \f
    [APIDOCS](https://habitica.com/apidoc/#api-User-UserCast)
    :param spell_name:
    :return:
    """
    log.debug(f"hopla cast {spell_name=}")
    request = PostCastRequest(spell=Spell(spell_name))
    response: requests.Response = request.post_spell()

    json_data: dict = get_data_or_exit(response)
    mana: float = HabiticaUser(json_data["user"]).get_mp()
    click.echo(f"{spell_name} casted successfully: {mana:.1f} mana left.")
