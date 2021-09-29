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

log = logging.getLogger()


@click.command()
@click.argument("spell_name", type=click.Choice(SpellData.single_arg_spells))
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
