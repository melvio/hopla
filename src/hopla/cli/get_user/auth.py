"""
The module with CLI code that handles the `hopla get-user user-authenticate` command.
"""

import logging

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import pass_user, HabiticaUser

log = logging.getLogger()

__SIGN_IN_OPTIONS = ["local", "google", "apple", "facebook"]
valid_auth_info_names = click.Choice([
    "username", "email", "profilename", *__SIGN_IN_OPTIONS, "all"
])


def auth_alias_to_official_habitica_name(auth_info_name: str):
    """
    Function that returns habitica official names for the CLI cmd:
    hopla get_user user-authenticate [alias]
    """
    if auth_info_name in ["e-mail", "mail"]:
        return "email"
    return auth_info_name


@click.command(
    context_settings={"token_normalize_func": auth_alias_to_official_habitica_name}
)
@click.argument("auth_info_name", type=valid_auth_info_names, default="all")
@pass_user
def auth(user: HabiticaUser, auth_info_name: str):
    """Get user authentication and identification info

    \b
    Examples
    ---
    \b
    # get a user's "local" (email based) sign in information
    $ hopla get-user auth local

    \b
    # get a user's apple/facebook/google sign in information
    $ hopla get-user auth apple
    $ hopla get-user auth facebook
    $ hopla get-user auth google

    \b
    # get the user email (assumes email based login)
    $ hopla get-user auth email


    """
    log.debug(f"hopla get-user auth auth_name={auth_info_name}")
    auth_data: dict = user.get_auth()

    if auth_info_name == "profilename":
        requested_data = user["profile"]["name"]
    elif auth_info_name == "username":
        requested_data = auth_data["local"]["username"]
    elif auth_info_name == "email":
        requested_data = auth_data["local"]["email"]
    elif auth_info_name in __SIGN_IN_OPTIONS:
        requested_data = auth_data[auth_info_name]
    else:
        requested_data = auth_data

    click.echo(JsonFormatter(requested_data).format_with_double_quotes())
    return requested_data
