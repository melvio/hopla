import os
from configparser import ConfigParser
from pathlib import Path


class AuthorizationConstants:
    CONFIG_SECTION_CREDENTIALS = "credentials"
    CONFIG_KEY_USER_ID = "user_id"
    CONFIG_KEY_API_TOKEN = "api_token"

    GLOBAL_ENV_VAR_XDG_CONFIG_HOME = "XDG_CONFIG_HOME"
    GLOBAL_ENV_VAR_HOPLA_AUTH_FILE = "HOPLA_AUTH_FILE"


class AuthorizationParser:
    def __init__(self):
        self.config_parser = ConfigParser()

    def _parse(self):
        if self.auth_file_exists():
            self.config_parser.read(self.auth_file)
        else:
            # TODO: have better user information (stack traces are not nice!)
            raise FileNotFoundError(f"could not find authorization file {self.auth_file}"
                                    f"Try running: `hopla set-hopla credentials")

    def auth_file_exists(self):
        return self.auth_file.exists \
               and self.auth_file.is_file()

    @property
    def auth_file(self) -> Path:
        """ Get the file with authorization"""
        auth_file: Path
        hopla_auth_file_env_var: str = os.environ.get(AuthorizationConstants.GLOBAL_ENV_VAR_HOPLA_AUTH_FILE)
        xdg_config_home_env_var: str = os.environ.get(AuthorizationConstants.GLOBAL_ENV_VAR_XDG_CONFIG_HOME)

        if hopla_auth_file_env_var:
            auth_file = Path(hopla_auth_file_env_var)
        elif xdg_config_home_env_var:
            auth_file = Path(xdg_config_home_env_var) / "hopla" / "auth.conf"
        else:
            auth_file = Path.home() / ".config" / "hopla" / "auth.conf"

        return auth_file.resolve()

    @property
    def user_id(self):
        # violating that @property should be cheap; However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_USER_ID)

    @property
    def api_token(self):
        # violating that @property should be cheap; However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_API_TOKEN)
