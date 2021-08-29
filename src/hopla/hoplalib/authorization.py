"""
Library code to handle Hopla's authorization, authentication and
identification.
"""

import uuid
import logging
import os
import sys
from configparser import ConfigParser
from pathlib import Path

import click

log = logging.getLogger()


class AuthorizationFileConstants:
    """Class with authorization and authentication related constants"""

    CONFIG_SECTION_CREDENTIALS = "credentials"
    """only section of the authorization file"""

    CONFIG_KEY_USER_ID = "user_id"
    """user id field in the hopla authorization file """
    CONFIG_KEY_API_TOKEN = "api_token"
    """api token field in the hopla authorization file """

    GLOBAL_ENV_VAR_HOPLA_AUTH_FILE = "HOPLA_AUTH_FILE"
    """ environment variable to overwrite the default auth file location """


def get_auth_file() -> Path:
    """ Get the file with authorization"""
    hopla_auth_file_env_var: str = \
        os.environ.get(AuthorizationFileConstants.GLOBAL_ENV_VAR_HOPLA_AUTH_FILE)
    if hopla_auth_file_env_var is not None:
        auth_file = Path(hopla_auth_file_env_var)
    else:
        auth_file = click.get_app_dir("hopla") / Path("auth.conf")

    return auth_file.resolve()


class AuthorizationHandler:
    """ TODO: violates SRP """

    def __init__(self, *, auth_file=get_auth_file()):
        self.config_parser = ConfigParser()
        self.auth_file = auth_file

    @property
    def user_id(self):
        """Return the user id to be used in habitica API requests"""
        # violating that @property should be cheap;
        # However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationFileConstants.CONFIG_KEY_USER_ID)

    @property
    def api_token(self):
        """Return the api token to be used in habitica API requests"""
        # violating that @property should be cheap;
        # However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationFileConstants.CONFIG_KEY_API_TOKEN)

    def auth_file_exists(self) -> bool:
        """Return True if the authentication file exists"""
        return self.auth_file.exists and self.auth_file.is_file()

    def set_hopla_credentials(self, *,
                              user_id: uuid.UUID,
                              api_token: uuid.UUID,
                              overwrite: bool = False):
        """set credentials in the credentials file

        :param user_id:
        :param api_token:
        :param overwrite:
        :return:
        """
        log.debug(f"set_hopla_credentials overwrite={overwrite}")
        if self.auth_file_exists() and overwrite is False:
            log.info(f"Auth file {self.auth_file} not recreated because it already exists")
            return

        self.create_auth_dir()
        with open(self.auth_file, mode="w", encoding="utf-8") as new_auth_file:
            self.config_parser.add_section(
                AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS)
            self.config_parser.set(
                section=AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS,
                option=AuthorizationFileConstants.CONFIG_KEY_USER_ID,
                value=str(user_id)
            )
            self.config_parser.set(
                section=AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS,
                option=AuthorizationFileConstants.CONFIG_KEY_API_TOKEN,
                value=str(api_token)
            )
            self.config_parser.write(new_auth_file)

        assert self.auth_file_is_valid(), f"{self.auth_file} is not valid"

    def auth_file_is_valid(self) -> bool:
        if self.auth_file_exists() is False:
            log.debug(f"{self.auth_file} does not exist")
            return False

        self.config_parser.read(self.auth_file)
        if self.config_parser.has_section(
                AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS) is False:
            log.debug(f"{self.auth_file} has no credentials section")
            return False

        if self._auth_file_has_user_id() is False:
            log.debug(f"{self.auth_file} has no user id")
            return False

        if self._auth_file_has_api_token() is False:
            log.debug(f"{self.auth_file} has no api token")
            return False

        return True

    def _auth_file_has_api_token(self) -> bool:
        """
        Return true if the auth file has an api_token value inside the [credentials] section
        """
        return self.config_parser.has_option(
            section=AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationFileConstants.CONFIG_KEY_API_TOKEN)

    def _auth_file_has_user_id(self) -> bool:
        """
        Return true if the auth file has an user_id value inside the [credentials] section
        """
        return self.config_parser.has_option(
            section=AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationFileConstants.CONFIG_KEY_USER_ID)

    def create_auth_dir(self):
        """Create the directory that the authorization file is supposed to be in"""
        Path.mkdir(self.auth_file.parent, parents=True, exist_ok=True)

    def _parse(self):
        if self.auth_file_exists():
            self.config_parser.read(self.auth_file)
        if self._auth_file_has_api_token() is False or self._auth_file_has_user_id() is False:
            print("no credentials found")
            print("Please run:")
            print("    hopla auth")
            sys.exit(1)  # TODO: handle this better
