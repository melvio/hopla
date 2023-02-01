"""
The module with CLI code that handles the `hopla get-user info` command.
"""

import logging

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import pass_user, HabiticaUser

log = logging.getLogger()

valid_info_names = click.Choice(["gems", "id", "notifications", "tags", "lastCron",
                                 "loginIncentives", "achievements",
                                 "guilds", "all"])


def info_alias_to_official_habitica_name(user_info_name: str) -> str:
    """Return the canonical habitica name"""
    if user_info_name in ["userid", "user-id"]:
        return "id"
    if user_info_name in ["gems", "gem"]:
        return "balance"
    return user_info_name


@click.command(context_settings={"token_normalize_func": info_alias_to_official_habitica_name})
@click.argument("user_info_name", type=valid_info_names, default="all")
@pass_user
def info(user: HabiticaUser,
         user_info_name: str) -> dict:
    """Return user information

    USER_INFO_NAME is the particular type of information that you want to return, by
    default "all".

    \b
    Examples:
    ---
    $ hopla get-user info                  # get all user info
    $ hopla get-user info gems             # get number of gems
    $ hopla get-user info id               # get user id
    $ hopla get-user info loginIncentives  # get number of times logged in

    \b
    # Examples with a jq filter:
    $ hopla get-user info | jq .items              # get all items of a user
    $ hopla get-user info | jq ".items.mounts"     # get all mounts
    $ hopla get-user info | jq ".inbox.messages"   # get personal messages

    \b
    # first get the notifications, then use jq to filter the notifications
    $ hopla get-user info notifications | jq '.[].type'

    \b
    # first get all tag objects and then only get the names of the tags
    $ hopla get-user info tags | jq '.[].name'

    \f
    [APIdocs](https://habitica.com/apidoc/#api-User-UserGet)

    :param user: HabiticaUser
    :param user_info_name:
    :return
    """
    log.debug(f"hopla get-user info {user_info_name=}")

    filtered_user = filter_on_user_info_name(user, user_info_name)

    user_str = JsonFormatter(filtered_user).format_with_double_quotes()
    click.echo(user_str)
    return filtered_user


def filter_on_user_info_name(user: HabiticaUser, user_info_name: str):
    """First time we filter the user.
       Returns whatever the result of filtering """
    if user_info_name == "gems":
        return user.get_gems()

    if user_info_name not in [None, "all"]:
        return user[user_info_name]

    return user.user_dict
