"""
The module with CLI code that handles the `hopla auth` command.
"""
import logging

import click

from hopla.hoplalib.authorization import AuthorizationHandler

log = logging.getLogger()


# TODO: --browser option
@click.command()
def auth():
    """Authorize yourself to access the Habitica.com API

    hopla auth allows you interactively providing access credentials.
    """
    log.debug("hopla auth")
    auth_handler = AuthorizationHandler()

    click.echo("Please enter your credentials.")
    click.echo("You can find them over at <https://habitica.com/user/settings/api>.")
    click.echo("They have the following format: 'c0ffee69-dada-feed-abb1-5ca1ab1ed004'.")
    click.echo("The user id can be found under 'User ID'.")
    user_id = click.prompt(text="Please paste your user ID here (press Ctrl-C to abort)",
                           type=click.UUID)

    api_token = click.prompt(text="Please paste your user API Token here (input remains hidden)",
                             type=click.UUID, hide_input=True)
    auth_handler.set_hopla_credentials(user_id=user_id, api_token=api_token, overwrite=True)

