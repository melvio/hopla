"""
The module with CLI code that handles the `hopla get user-auth` command.
"""

import logging

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get import pass_user, HabiticaUser

log = logging.getLogger()

# username -> 'data.auth.local.username':
# * Your username is used for invitations, @mentions in chat, and messaging.
#   * It:
#     + must be 1 to 20 characters,
#     + must contain only letters a to z, numbers 0 to 9, hyphens, or underscores, and
#     + cannot include any inappropriate terms.
# * is changeable at '<https://habitica.com/user/settings/site>' 'Change Display Name'

# profilename -> 'data.profile.name'
# *  is changeable at '<https://habitica.com/user/settings/site>' under 'Change Display Name'
# profilename is not really in the .data.auth section of /user.. but fits well here
# TODO: probably better to remove profilename here regardless


__SIGN_IN_OPTIONS = ["local", "google", "apple", "facebook"]
valid_auth_info_names = click.Choice([
    "username", "email", "profilename", *__SIGN_IN_OPTIONS, "all"
])


def auth_alias_to_official_habitica_name(auth_info_name: str):
    """
    Function that returns habitica official names for the CLI cmd:
    hopla get user-auth [alias]
    """
    if auth_info_name in ["e-mail", "mail"]:
        return "email"
    return auth_info_name


@click.command(context_settings=dict(token_normalize_func=auth_alias_to_official_habitica_name))
@click.argument("auth_info_name", type=valid_auth_info_names, default="all")
@pass_user
def user_auth(user: HabiticaUser, auth_info_name: str):
    """Get user authentication and identification info

    NOTE: `hopla get user-auth` currently only supports email-based
    logins (not 3rd party logins such as google SSO). As a workaround, you
    can use `hopla get user-info --filter|-f FILTER_STRING`. For example, to
    get google SSO credentials you can use:

    \b
    Examples
    ---
    \b
    # get "local" (email based) sign in information
    $ hopla get user-auth local

    \b
    # get apple/facebook/google sign in information
    $ hopla get user-auth apple
    $ hopla get user-auth facebook
    $ hopla get user-auth google

    \b
    # get email (assumes email based login)
    $ hopla get user-auth email


    """
    log.debug(f"hopla get user-auth auth={auth_info_name}")
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
