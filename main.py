#!/usr/bin/env python3

import sys
import click
import os
import logging
from pathlib import Path
from argparse import ArgumentParser

from hopla.hoplalib.Authorization import AuthorizationHandler


def setup_logging() -> logging.Logger:
    """Setup python logging for the entire hopla project"""
    # https://docs.python.org/3.8/howto/logging.html#logging-basic-tutorial
    logging.basicConfig(
        format='[%(levelname)s][%(filename)s - %(asctime)s] %(message)s',
        level=logging.DEBUG,
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    return logging.getLogger(__name__)


log = setup_logging()


# https://docs.python.org/3/library/dataclasses.html
class HoplaEnvironment:
    def add_auth_information_to_env(self, start_env: dict):
        auth_info = AuthorizationHandler()
        auth_file_path = str(auth_info.auth_file)
        # TODO: instead of using strings directly, bring this under an object
        #       that does validation of UUIDs etc.
        start_env["auth_file_path"] = auth_file_path
        start_env["user_id"] = auth_info.user_id
        start_env["api_token"] = auth_info.api_token

        log.debug(f"auth_file={auth_file_path}")

        return start_env

    def create_hopla_env(self, script_dirname: str):
        library_dir = script_dirname + "/library"
        hopla_env = os.environ
        hopla_env["script_dirname"] = script_dirname
        hopla_env["library_dir"] = library_dir
        hopla_env = self.add_auth_information_to_env(dict(hopla_env))

        return hopla_env


from hopla.subgroups.add import add
from hopla.subgroups.api import api
from hopla.subgroups.set import set
from hopla.subcommands.version import version
from hopla.subcommands.auth import auth
from hopla.subgroups.buy import buy
from hopla.subgroups.get import get


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def hopla():
    pass


if __name__ == "__main__":
    log.debug(f"start application with arguments: {sys.argv}")
    script_dirname = os.path.dirname(Path(__file__).resolve())
    hopla_env = HoplaEnvironment().create_hopla_env(script_dirname=script_dirname)
    hopla.add_command(add)
    hopla.add_command(api)
    hopla.add_command(set)
    hopla.add_command(version)
    hopla.add_command(auth)
    hopla.add_command(buy)
    hopla.add_command(get)
    hopla()
