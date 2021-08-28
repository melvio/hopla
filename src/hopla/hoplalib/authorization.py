"""
Library code to handle Hopla's authorization, authentication and
identification.
"""

import logging
import os
from configparser import ConfigParser
from pathlib import Path

log = logging.getLogger()


class AuthorizationConstants:
    """Class with authorization and authentication related constants"""
    CONFIG_SECTION_CREDENTIALS = "credentials"
    CONFIG_KEY_USER_ID = "user_id"
    CONFIG_KEY_API_TOKEN = "api_token"

    GLOBAL_ENV_VAR_XDG_CONFIG_HOME = "XDG_CONFIG_HOME"
    GLOBAL_ENV_VAR_HOPLA_AUTH_FILE = "HOPLA_AUTH_FILE"


class AuthorizationHandler:
    """ TODO: violates SRP """

    def __init__(self):
        self.config_parser = ConfigParser()

    @property
    def auth_file(self) -> Path:
        """ Get the file with authorization"""
        auth_file: Path
        hopla_auth_file_env_var: str = os.environ.get(
            AuthorizationConstants.GLOBAL_ENV_VAR_HOPLA_AUTH_FILE)
        xdg_config_home_env_var: str = os.environ.get(
            AuthorizationConstants.GLOBAL_ENV_VAR_XDG_CONFIG_HOME)

        if hopla_auth_file_env_var:
            auth_file = Path(hopla_auth_file_env_var)
        elif xdg_config_home_env_var:
            auth_file = Path(xdg_config_home_env_var) / "hopla" / "auth.conf"
        else:
            auth_file = Path.home() / ".config" / "hopla" / "auth.conf"

        # TODO: check if resolve could fail if these dirs dont exist
        return auth_file.resolve()

    @property
    def auth_dir(self) -> Path:
        parent = self.auth_file.parent
        # TODO: cleanup with unittest
        assert parent.exists() and parent.is_dir(), f"expected dir {parent} to exist"
        return parent

    @property
    def user_id(self):
        # violating that @property should be cheap;
        # However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[
            AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_USER_ID)

    @property
    def api_token(self):
        # violating that @property should be cheap;
        # However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[
            AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_API_TOKEN)

    def auth_file_exists(self):
        return self.auth_file.exists and self.auth_file.is_file()

    def set_hopla_credentials(self, *, overwrite: bool = False):
        log.debug(f"set_hopla_credentials overwrite={overwrite}")
        if self.auth_file_exists() and overwrite is False:
            log.info(
                f"Auth file {self.auth_file} not recreated because it already exists")
            return

        # TODO: with mode=w here, we are essentially creating this empty auth file twice
        self._create_empty_auth_file()

        user_id, api_token = self.request_user_credentials()
        with open(self.auth_file, mode="w") as new_auth_file:
            self.config_parser.add_section(
                AuthorizationConstants.CONFIG_SECTION_CREDENTIALS)
            self.config_parser.set(
                section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
                option=AuthorizationConstants.CONFIG_KEY_USER_ID,
                value=user_id
            )
            self.config_parser.set(
                section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
                option=AuthorizationConstants.CONFIG_KEY_API_TOKEN,
                value=api_token
            )
            self.config_parser.write(new_auth_file)

        assert self.auth_file_is_valid(), f"{self.auth_file} is not valid"

    def auth_file_is_valid(self) -> bool:
        if self.auth_file_exists() is False:
            log.debug(f"{self.auth_file} does not exist")
            return False

        self.config_parser.read(self.auth_file)
        if self.config_parser.has_section(
                AuthorizationConstants.CONFIG_SECTION_CREDENTIALS) is False:
            log.debug(f"{self.auth_file} has no credentials section")
            return False
        elif self._auth_file_has_user_id() is False:
            log.debug(f"{self.auth_file} has no user id")
            return False
        elif self._auth_file_has_api_token() is False:
            log.debug(f"{self.auth_file} has no api token")
            return False
        else:
            return True

    def _auth_file_has_api_token(self) -> bool:
        return self.config_parser.has_option(
            section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationConstants.CONFIG_KEY_API_TOKEN)

    def _auth_file_has_user_id(self) -> bool:
        return self.config_parser.has_option(
            section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationConstants.CONFIG_KEY_USER_ID)

    def _create_empty_auth_file(self):
        self._create_auth_dir()
        with open(self.auth_file, mode="w"):
            pass  # no need to write to it, just create it

    def _create_auth_dir(self):
        Path.mkdir(self.auth_dir, parents=True, exist_ok=True)

    def request_user_credentials(self) -> (str, str):
        print("Please enter your credentials")
        print(
            "You can find them over at <https://habitica.com/user/settings/api> ")
        print(
            "The user id can be found under 'User ID' and you need to click 'Show API Token'")

        try:
            # validate input:
            # TODO: look into https://docs.python.org/3/library/uuid.html
            uuid_user_id: str = self._request_for_user_id()
            uuid_api_token: str = self._request_for_api_token()
        except (EOFError, KeyboardInterrupt) as e:
            log.debug(f"user send a EOF: {e}")
            print("aborted the creation of a new authentication file")
            exit(0)

        return uuid_user_id, uuid_api_token

    def _request_for_user_id(self) -> str:
        return input("Please paste your user id here: ")

    def _request_for_api_token(self) -> str:
        return input("Please paste your api token id here: ")

    def _parse(self):
        if self.auth_file_exists():
            self.config_parser.read(self.auth_file)
        if self._auth_file_has_api_token() is False or self._auth_file_has_user_id() is False:
            print("no credentials found")
            print("Please run:")
            print("    hopla auth")
            exit(1)
