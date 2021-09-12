"""
The module with CLI code that handles the `hopla authenticate` command.
"""
import logging
from uuid import UUID
from dataclasses import dataclass

import click

from hopla.hoplalib.authorization import AuthorizationHandler

log = logging.getLogger()


@click.command()
def authenticate():
    """Authorize yourself to access the Habitica.com API.

    hopla authenticate allows you to interactively provide access credentials.
    """
    log.debug("hopla authenticate")

    hopla_user_credentials: HoplaUserCredentials = request_user_for_credentials()

    AuthorizationHandler().set_hopla_credentials(
        user_id=hopla_user_credentials.user_id,
        api_token=hopla_user_credentials.api_token,
        overwrite=True
    )


@dataclass(frozen=True)
class HoplaUserCredentials:
    """Class representing the user's credentials"""
    user_id: UUID
    api_token: UUID


def request_user_for_credentials() -> HoplaUserCredentials:
    """Request the user for the user id and api token"""
    click.echo("Please enter your credentials.")
    click.echo("You can find them over at <https://habitica.com/user/settings/api>.")
    click.echo("They have the following format: 'c0ffee69-dada-feed-abb1-5ca1ab1ed004'.")
    click.echo("The user id can be found under 'User ID'.")
    user_id = click.prompt(text="Please paste your user ID here (press Ctrl-C to abort)",
                           type=click.UUID)
    api_token = click.prompt(text="Please paste your user API Token here (input remains hidden)",
                             type=click.UUID, hide_input=True)
    return HoplaUserCredentials(user_id=user_id, api_token=api_token)
