#!/usr/bin/env python3
import json

import requests
import configparser
from configparser import ConfigParser
from argparse import ArgumentParser, Namespace
import os
from pathlib import Path

api_version = "v3"
domain = "https://habitica.com"
base_url = f"{domain}/api/{api_version}/user"
custom_day_start_url = f"{base_url}/custom-day-start"


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


class RequestHeaders:
    CONTENT_TYPE = "Content-Type"
    CONTENT_TYPE_JSON = "application/json"
    X_CLIENT = "x-client"
    X_API_USER = "x-api-user"
    X_API_KEY = "x-api-key"
    X_CLIENT_VALUE = "79551d98-31e9-42b4-b7fa-9d89b0944319-hopla"

    def __init__(self, auth_parser: AuthorizationParser = None):
        if auth_parser:
            self.hopla_auth_parser = auth_parser
        else:
            self.hopla_auth_parser = AuthorizationParser()

    def get_default_request_headers(self):
        return {
            RequestHeaders.CONTENT_TYPE: RequestHeaders.CONTENT_TYPE_JSON,
            RequestHeaders.X_CLIENT: RequestHeaders.X_CLIENT_VALUE,
            RequestHeaders.X_API_USER: self.hopla_auth_parser.user_id,
            RequestHeaders.X_API_KEY: self.hopla_auth_parser.api_token
        }


headers = RequestHeaders().get_default_request_headers()


class DayStartArgumentParser:
    DAY_START_USER_ARGUMENT = "day_start"

    def __init__(self, arg_parser: ArgumentParser = None):
        if arg_parser:
            self.arg_parser = arg_parser
        else:
            self.arg_parser = ArgumentParser()

        self.arg_parser.add_argument(
            DayStartArgumentParser.DAY_START_USER_ARGUMENT,
            nargs="?",
            help="the hour to start your habitica day",
            type=int,
            default=0
        )

    @property
    def day_start(self):
        # parsing every time is cheap; it is just 1 value the user supplies
        args: Namespace = self.arg_parser.parse_args()
        return args.day_start


day_start_arg_parser = DayStartArgumentParser()


class DayStartJsonCreator:
    DAY_START_KEY = "dayStart"

    def __init__(self, *, day_start: int):
        self.day_start = day_start

    def _create_post_content(self) -> dict:
        return {DayStartJsonCreator.DAY_START_KEY: self.day_start}

    @property
    def json_content(self) -> str:
        post_content: dict = self._create_post_content()
        # todo: instead of asserts use unittests
        assert len(post_content) != 0, "created json is empty"

        return json.dumps(post_content)

json_content = DayStartJsonCreator(day_start=day_start_arg_parser.day_start).json_content

# set to midnight:
# python3 day-start.py

# set to 1 AM
# python3 day-start.py 1

response: requests.Response = requests.post(
    url=custom_day_start_url,
    headers=headers,
    data=json_content
)

print(response.json())
print(response.headers)
print(str(response.content))
