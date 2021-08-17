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


class HoplaAuthorization:

    def auth_file_exists(self):
        return self.auth_file.exists \
               and self.auth_file.is_file()

    @property
    def auth_file(self):
        """ Get the file with authorization"""
        auth_file: Path
        hopla_auth_file_env_var = os.environ.get("HOPLA_AUTH_FILE")
        xdg_config_home_env_var = os.environ.get("XDG_CONFIG_HOME")

        if hopla_auth_file_env_var:
            auth_file = Path(hopla_auth_file_env_var)
        elif xdg_config_home_env_var:
            auth_file = Path(xdg_config_home_env_var) / "hopla" / "auth.conf"
        else:
            auth_file = Path.home() / ".config" / "hopla" / "auth.conf"

        return auth_file.resolve()


config = ConfigParser()

AUTH_FILE: Path = HoplaAuthorization().auth_file
print(f"exists={HoplaAuthorization().auth_file_exists()}")
config.read(AUTH_FILE)

print(config)
print(config.sections())
print(config["credentials"])

credentials = config["credentials"]
user_id = credentials.get("user_id")
api_token = credentials.get("api_token")
x_client_id = "79551d98-31e9-42b4-b7fa-9d89b0944319-hopla"

headers = {
    "Content-Type": "application/json",
    "x-client": x_client_id,
    "x-api-user": user_id,
    "x-api-key": api_token
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
