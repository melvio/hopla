"""
The module with CLI code that handles the `hopla get-user info` command.
"""

import logging

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import pass_user, HabiticaUser

log = logging.getLogger()

valid_info_names = click.Choice(["gems", "id", "notifications", "tags", "lastCron",
                                 "loginIncentives", "all"])


def info_alias_to_official_habitica_name(user_info_name: str) -> str:
    """Return the canonical habitica name"""
    if user_info_name in ["userid", "user-id"]:
        return "id"
    if user_info_name in ["gems", "gem"]:
        return "balance"
    return user_info_name


@click.command(context_settings=dict(token_normalize_func=info_alias_to_official_habitica_name))
# TODO: consider upgrading to full-blown jq and dont handle this yourself
@click.argument("user_info_name", type=valid_info_names, default="all")
@click.option("--filter", "-f", "filter_string", metavar="FILTER_STRING",
              help="a comma seperated list of keys")
@pass_user
def info(user: HabiticaUser, user_info_name: str, filter_string: str) -> dict:
    """Return user information

    If no FILTER_STRING is given, get all the user's info.
    Otherwise, return the result of filtering the user's info with the
    specified FILTER_STRING.

    USER_INFO_NAME the particular type of information that you want to return, by
    default "all".


    \b
    [BNF](https://en.wikipedia.org/wiki/Backus-Naur-Form)
    for the FILTER_STRING:

    \b
        filter_keys ::= [filter_keys]?[,filter_keys]*
        filter_keys ::= filter_keys[.filter_keys]*

    \b
    Examples:
    ---
    # get-user all user info
    $ hopla get-user info

    \b
    # get-user number of gems
    $ hopla get-user info gems

    \b
    # get-user user id
    $ hopla get-user info id

    \b
    # get-user number of times logged in
    $ hopla get-user info loginIncentives

    \b
    # get-user all items of a user:
    $ hopla get-user info --filter=items

    \b
    # get-user all mounts
    $ hopla get-user info --filter "items.mounts"

    \b
    # get-user all mounts+pets
    $ hopla get-user info --filter "items.mounts,items.pets"

    \b
    # get-user streaks+completed quests
    $ hopla get-user info -f "achievements.streak,achievements.quests"

    \b
    # get-user contributor status, cron-count, profile description, and user id
    $ hopla get-user info -f "contributor, flags.cronCount, profile.blurb, id"

    \b
    # get-user last free rebirth, day start (in hours), timezone offset (in minutes), and
    # account creation time
    $ hopla get-user info -f 'flags.lastFreeRebirth, preferences.dayStart, preferences.timezoneOffset, auth.timestamps.created'   # pylint: disable=line-too-long

    \f
    [APIdocs](https://habitica.com/apidoc/#api-User-UserGet)

    :param user: HabiticaUser
    :param user_info_name:
    :param filter_string: string to filter the user dict on (e.g. "achievements.streak,purchased.plan")
    :return
    """
    log.debug(f"hopla get-user info user_info_name={user_info_name} filter={filter_string}")

    if filter_string:
        requested_user_data: dict = user.filter_user(filter_string)
    elif user_info_name == "all":
        requested_user_data: dict = user.user_dict
    elif user_info_name == "gems":
        gems = user.get_gems()
        requested_user_data: dict = {"gems": gems}
    else:
        requested_user_data: dict = user.filter_user(user_info_name)

    user_str = JsonFormatter(requested_user_data).format_with_double_quotes()
    click.echo(user_str)
    return requested_user_data
