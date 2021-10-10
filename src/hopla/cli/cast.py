#!/usr/bin/env python3
"""
The module with CLI code that handles the `hopla cast` command.
"""
import logging

import click
import requests

from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.cast.castcontroller import PostCastRequest
from hopla.hoplalib.cast.spellmodel import Spell, SpellData
from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.throttling import ApiRequestThrottler

log = logging.getLogger()


@click.command()
@click.argument("spell_name", type=click.Choice(SpellData.single_arg_spells))
@click.option("--until-out-of-mana", "-u", is_flag=True, default=False,
              help="Keep casting the specified spell until there is insufficient mana left.")
def cast(spell_name: str, until_out_of_mana: bool) -> None:
    """Cast a spell.

    SPELL_NAME the name of the spell to cast

    Currently, there is only support for spells that are not cast on one
    single task.

    \b
    Examples:
    ---
    # Cast heal all.
    $ hopla cast heallAll

    \b
    # Cast tools of trade until you don't have enough mana left to continue casting.
    $ hopla cast toolsOfTrade --until-out-of-mana

    \b
    # Cast earthquake until you don't have enough mana left to continue casting.
    $ hopla cast -u earth

    \f
    [APIDOCS](https://habitica.com/apidoc/#api-User-UserCast)
    :param spell_name: The spell to cast.
    :param until_out_of_mana: Flag that indicates that the spell should be repeated until
     there is insufficient mana left to keep casting the specified spell.
    :return:
    """
    log.debug(f"hopla cast {spell_name=}")

    spell = Spell(spell_name)
    mana: float = cast_spell_or_exit(spell)

    if until_out_of_mana is True:
        times: int = times_until_out_of_mana(spell, remaining_mana=mana)
        dispatcher = ApiRequestThrottler([lambda: cast_spell_or_exit(spell) for _ in range(times)])
        dispatcher.execute_all_requests()


def times_until_out_of_mana(spell: Spell, *, remaining_mana: float) -> int:
    """
    Return how often you can still cast the spell before you run out of mana.
    """
    return int(remaining_mana / spell.mana_required)


def cast_spell_or_exit(spell: Spell) -> float:
    """
    Cast the given spell by executing an API request.
    :param spell:
    :return:
    """
    request = PostCastRequest(spell=spell)
    response: requests.Response = request.post_spell()
    json_data: dict = get_data_or_exit(response)
    mana = HabiticaUser(json_data["user"]).get_mp()
    click.echo(f"{spell.name} casted successfully: {mana:.1f} mana left.")
    return mana
