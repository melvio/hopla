"""
The module with CLI code that handles the `hopla get-user stats` command.
"""

import logging
from typing import Any

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import pass_user, HabiticaUser

log = logging.getLogger()

valid_stat_names = click.Choice(["hp", "mp", "exp", "gp", "lvl", "class",
                                 "maxMP",
                                 "int", "str", "per", "con",
                                 "all"])


def stat_alias_to_official_habitica_name(stat_name: str) -> str:  # noqa: C901 (Mccabe too high)
    """Turn typos and similar namings into stats recognized by the habitica API.

    :param stat_name:
    :return:
    """
    # pylint: disable=too-many-return-statements,too-many-branches
    if stat_name in ["mana", "mana-points", "manapoints"]:
        return "mp"
    if stat_name in ["maxMp", "maxmp"]:
        return "maxMP"
    if stat_name in ["health", "healthpoints"]:
        return "hp"
    if stat_name in ["xp", "experience"]:
        return "exp"
    if stat_name in ["gold"]:
        return "gp"
    if stat_name in ["level"]:
        return "lvl"
    if stat_name in ["intelligence"]:
        return "int"
    if stat_name in ["strength"]:
        return "str"
    if stat_name in ["perception"]:
        return "per"
    if stat_name in ["constitution"]:
        return "con"

    return stat_name


@click.command(
    context_settings={"token_normalize_func": stat_alias_to_official_habitica_name}
)
@click.argument("stat_name", type=valid_stat_names, default="all")
@pass_user
def stats(user: HabiticaUser, stat_name: str) -> Any:
    """Get the stats of a user

    \b
    Examples
    ---
    # get all user stats
    $ hopla get-user stats
    $ hopla get-user stats all

    \b
    # get-user mana, health, level
    $ hopla get-user stats mp
    $ hopla get-user stats hp
    $ hopla get-user stats lvl
    """
    log.debug(f"hopla get-user stats {stat_name=}")

    stats_data = user.get_stats()
    if stat_name == "all":
        requested_user_data = stats_data
    else:
        requested_user_data = stats_data[stat_name]
    click.echo(JsonFormatter(requested_user_data).format_with_double_quotes())
    return requested_user_data
