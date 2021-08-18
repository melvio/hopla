#!/usr/bin/env python3
import json

import requests
import configparser
from configparser import ConfigParser
from argparse import ArgumentParser
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


class HoplaAuthorizationParser:

    def __init__(self):
        self.config_parser = ConfigParser()

    def initialize(self):
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
        hopla_auth_file_env_var = os.environ.get(AuthorizationConstants.GLOBAL_ENV_VAR_HOPLA_AUTH_FILE)
        xdg_config_home_env_var = os.environ.get(AuthorizationConstants.GLOBAL_ENV_VAR_XDG_CONFIG_HOME)

        if hopla_auth_file_env_var:
            auth_file = Path(hopla_auth_file_env_var)
        elif xdg_config_home_env_var:
            auth_file = Path(xdg_config_home_env_var) / "hopla" / "auth.conf"
        else:
            auth_file = Path.home() / ".config" / "hopla" / "auth.conf"

        return auth_file.resolve()

    @property
    def user_id(self):
        return self.config_parser[AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_USER_ID)

    @property
    def api_token(self):
        return self.config_parser[AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_API_TOKEN)


hopla_auth_parser = HoplaAuthorizationParser()
hopla_auth_parser.initialize()

x_client_id = "79551d98-31e9-42b4-b7fa-9d89b0944319-hopla"

headers = {
    "Content-Type": "application/json",
    "x-client": x_client_id,
    "x-api-user": hopla_auth_parser.user_id,
    "x-api-key": hopla_auth_parser.api_token
}

arg_parser = ArgumentParser()
day_start_key = "day_start"
arg_parser.add_argument(
    day_start_key,
    nargs="?",
    help="the hour to start your habitica day",
    type=int,
    default=0
)

args = arg_parser.parse_args()
post_content = {"dayStart": args.day_start}

# set to midnight:
# python3 day-start.py

# set to 1 AM
# python3 day-start.py 1
json_content = json.dumps(post_content)
print("json_content", json_content)

response: requests.Response = requests.post(
    url=custom_day_start_url,
    headers=headers,
    data=json_content
)

print(response.json())
print(response.headers)
print(str(response.content))
