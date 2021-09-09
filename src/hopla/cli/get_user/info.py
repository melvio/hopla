"""
The module with CLI code that handles the `hopla get-user info` command.
"""

import logging

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import pass_user, HabiticaUser
from hopla.hoplalib.dict_filters import click_jq_filter_option, JqFilter

log = logging.getLogger()

valid_info_names = click.Choice(["gems", "id", "notifications", "tags", "lastCron",
                                 "loginIncentives", "achievements",
                                 "all"])


def info_alias_to_official_habitica_name(user_info_name: str) -> str:
    """Return the canonical habitica name"""
    if user_info_name in ["userid", "user-id"]:
        return "id"
    if user_info_name in ["gems", "gem"]:
        return "balance"
    return user_info_name


@click.command(context_settings=dict(token_normalize_func=info_alias_to_official_habitica_name))
@click.argument("user_info_name", type=valid_info_names, default="all")
@click_jq_filter_option()
@pass_user
def info(user: HabiticaUser,
         user_info_name: str,
         jq_filter: str) -> dict:
    """Return user information

    USER_INFO_NAME is the particular type of information that you want to return, by
    default "all".

    JQ_FILTER is a valid `jq` filter.
    USER_INFO_DICT get the relevant data from the user. Then the JQ_FILTER is
    applied on the that result.

    \b
    [BNF](https://en.wikipedia.org/wiki/Backus-Naur-Form)
    for the FILTER_STRING:

    \b
        filter_keys ::= [filter_keys]?[,filter_keys]*
        filter_keys ::= filter_keys[.filter_keys]*

    \b
    Examples:
    ---
    $ hopla get-user info                  # get all user info
    $ hopla get-user info gems             # get number of gems
    $ hopla get-user info id               # get user id
    $ hopla get-user info loginIncentives  # get number of times logged in

    \b
    # Examples with a jq filter:
    $ hopla get-user info --jq-filter=.items            #  get all items of a user
    $ hopla get-user info --jq-filter ".items.mounts"   # get-user all mounts

    \b
    # first get the notifications, then use jq to filter the notifications
    $ hopla get-user info notifications -j '.[].type'

    # first get all tag objects and then only get the names of the tags
    # HMM TODO: figure out the difference between:
    hopla get-user info tags -j '.[].name'
    hopla get-user info tags | jq '.[].name'

    \f
    [APIdocs](https://habitica.com/apidoc/#api-User-UserGet)

    :param jq_filter:
    :param user: HabiticaUser
    :param user_info_name:
    :return
    """
    log.debug(f"hopla get-user info \n"
              f"{user_info_name=} {jq_filter=}")

    prefilter_user = prefilter_on_user_info_name(user, user_info_name)
    log.debug(f"{prefilter_user}")

    requested_user_data = postfilter(prefilter_user, jq_filter)

    user_str = JsonFormatter(requested_user_data).format_with_double_quotes()
    click.echo(user_str)
    return requested_user_data


def postfilter(prefiltered_user, jq_filter: str):
    """Second time we filter the user"""
    if jq_filter is None:
        return prefiltered_user

    jq_filter = JqFilter(jq_filter_spec=jq_filter)
    return jq_filter(json_dict=prefiltered_user)


def prefilter_on_user_info_name(user: HabiticaUser, user_info_name: str):
    """First time we filter the user.
       Returns whatever the result of filtering """
    if user_info_name == "gems":
        return {"gems": user.get_gems()}

    if user_info_name == "all":
        return user.user_dict

    if user_info_name is not [None, "all"]:
        return user[user_info_name]

    return user.user_dict
