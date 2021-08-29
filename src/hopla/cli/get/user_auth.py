"""
The module with CLI code that handles the `hopla get user-auth` command.
"""

import logging

import click

from hopla.hoplalib.clickhelper import data_on_success_else_exit
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get import HabiticaUserRequest, HabiticaUser

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

valid_auth_info_names = click.Choice(["username", "email", "profilename", "all"])


def auth_alias_to_official_habitica_name(auth_info_name: str):
    if auth_info_name in ["e-mail", "mail"]:
        return "email"
    return auth_info_name


@click.command(context_settings=dict(token_normalize_func=auth_alias_to_official_habitica_name))
@click.argument("auth_info_name", type=valid_auth_info_names, default="all")
def user_auth(auth_info_name: str):
    """Get user authentication and identification info

    NOTE: `hopla get user-auth` currently only supports email-based
    logins (not 3rd party logins such as google SSO). As a workaround, you
    can use `hopla get user-info --filter|-f FILTER_STRING`. For example, to
    get google SSO credentials you can use:

    \b
    Examples
    ---
    # get email
    hopla get user-auth email

    \b
    # workaround for SSO information
    hopla get user-info -f "auth.google"

    """
    log.debug(f"hopla get user-auth auth={auth_info_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = data_on_success_else_exit(response)
    user = HabiticaUser(user_dict=response_data)

    json_data_auth: dict = user.get_auth()

    if auth_info_name == "all":
        click.echo(JsonFormatter(json_data_auth).format_with_double_quotes())
        return json_data_auth

    if auth_info_name == "profilename":
        profile_name = response_data["profile"]["name"]
        click.echo(JsonFormatter(profile_name).format_with_double_quotes())
        return profile_name

    # TODO no support for non-local data yet (e.g. google SSO)
    #      e.g. use hopla get user-info -f "auth.google" as workaround
    auth_info = json_data_auth["local"][auth_info_name]
    click.echo(JsonFormatter(auth_info).format_with_double_quotes())
    return auth_info
