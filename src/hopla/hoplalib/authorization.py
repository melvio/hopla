"""
Library code to handle Hopla's authorization, authentication and
identification.
"""

import uuid
import logging
import sys
from configparser import ConfigParser
from pathlib import Path
from hopla.hoplalib.common import get_configuration_dirpath, EnvironmentVariables

log = logging.getLogger()


class AuthorizationFileConstants:
    """Class with authorization and authentication related constants"""

    CONFIG_SECTION_CREDENTIALS = "credentials"
    """only section of the authorization file"""

    CONFIG_KEY_USER_ID = "user_id"
    """user id field in the hopla authorization file """
    CONFIG_KEY_API_TOKEN = "api_token"
    """api token field in the hopla authorization file """


class HoplaAuthFile:
    """
    Class representing the Hopla Auth file. This file keeps the user uuid and user
    api token separate from other hopla configuration.
    """
    def __init__(self):
        self.global_env_var_hopla_auth_file = EnvironmentVariables.HOPLA_AUTH_FILE

    @property
    def file_path(self) -> Path:
        """ Get the file with authorization"""
        if self.global_env_var_hopla_auth_file is not None:
            auth_file = Path(self.global_env_var_hopla_auth_file)
        else:
            auth_file = get_configuration_dirpath() / "authenticate.conf"

        return auth_file.resolve()

    def exists(self) -> bool:
        """Return True if the authentication file exists"""
        return self.file_path.exists() and self.file_path.is_file()

    def create_auth_dir(self):
        """Create the directory that the authorization file is supposed to be in"""
        Path.mkdir(self.file_path.parent, parents=True, exist_ok=True)


class AuthorizationHandler:
    """
    This class *should* only get and set values in the hopla authorization file.
    """

    def __init__(self, *, auth_file: HoplaAuthFile = None):
        self.config_parser = ConfigParser()
        if auth_file is None:
            self.auth_file = HoplaAuthFile()
        else:
            self.auth_file = auth_file

    @property
    def user_id(self):
        """Return the user id to be used in habitica API requests"""
        self._parse()
        return self.config_parser[AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationFileConstants.CONFIG_KEY_USER_ID)

    @property
    def api_token(self):
        """Return the api token to be used in habitica API requests"""
        self._parse()
        return self.config_parser[AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationFileConstants.CONFIG_KEY_API_TOKEN)

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
        if self.auth_file.exists() and overwrite is False:
            log.info(f"Auth file {self.auth_file} not recreated because it already exists")
            return

        self.auth_file.create_auth_dir()
        with open(self.auth_file.file_path, mode="w", encoding="utf-8") as new_auth_file:
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
        """
        Return True when the authenticate file exists, has a [credentials] section with
        a user id and api token field in it.
        """
        if self.auth_file.exists() is False:
            log.debug(f"{self.auth_file} does not exist")
            return False

        self.config_parser.read(self.auth_file.file_path)
        if self.config_parser.has_section(
                AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS) is False:
            log.debug(f"{self.auth_file} has no "
                      f"{AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS} section")
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
        Return true if the authenticate file has an api_token value
        inside the [credentials] section.
        """
        return self.config_parser.has_option(
            section=AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationFileConstants.CONFIG_KEY_API_TOKEN)

    def _auth_file_has_user_id(self) -> bool:
        """
        Return true if the authenticate file has an user_id
        value inside the [credentials] section.
        """
        return self.config_parser.has_option(
            section=AuthorizationFileConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationFileConstants.CONFIG_KEY_USER_ID)

    def _parse(self):
        if self.auth_file.exists():
            self.config_parser.read(self.auth_file.file_path)
        if self._auth_file_has_api_token() is False or self._auth_file_has_user_id() is False:
            print("no credentials found")
            print("Please run:")
            print("    hopla authenticate")
            sys.exit(1)
