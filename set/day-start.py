#!/usr/bin/env python3

import requests
import configparser
from configparser import ConfigParser
import os
from pathlib import Path


api_version = "v3"
domain = "https://habitica.com"
base_url = f"{domain}/api/{api_version}/user"


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

url="https://habitica.com/api/v3/user?userFields=items.mounts"

response = requests.get(url, headers=headers)
print(response.json())


# response = requests.get(base_url, headers=headers)
# print(response.json())
# print(response.headers)
# print(response.content)
