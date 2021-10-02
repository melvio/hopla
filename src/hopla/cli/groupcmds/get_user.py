"""
The module with CLI code that handles the `hopla get` group command.
"""
import logging

import click

from hopla.hoplalib.user.usercontroller import HabiticaUserRequest
from hopla.hoplalib.user.usermodels import HabiticaUser

log = logging.getLogger()

pass_user = click.make_pass_decorator(HabiticaUser)


@click.group()
@click.pass_context
def get_user(ctx: click.Context) -> HabiticaUser:
    """
    GROUP for getting user information from Habitica.
    """
    log.debug("hopla get-user")
    user: HabiticaUser = HabiticaUserRequest().request_user_data_or_exit()
    ctx.obj = user
    return user
