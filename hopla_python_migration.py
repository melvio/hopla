#!/usr/bin/env python3

import sys
import subprocess
import os
import logging
from pathlib import Path

# TODO: temporary, while hopla is in beta
try:
    # cmdline
    from hoplalib.Authorization import AuthorizationHandler
except:
    # jetbrains
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


def add_auth_information_to_env(start_env: dict):
    auth_info = AuthorizationHandler()
    auth_file_path = str(auth_info.auth_file)
    # TODO: instead of using strings directly, bring this under an object
    #       that does validation of UUIDs etc.
    start_env["auth_file_path"] = auth_file_path
    start_env["user_id"] = auth_info.user_id
    start_env["api_token"] = auth_info.api_token

    log.debug(f"auth_file={auth_file_path}")

    return start_env


def create_hopla_env(script_dirname: str):
    library_dir = script_dirname + "/library"
    hopla_env = os.environ
    hopla_env["script_dirname"] = script_dirname
    hopla_env["library_dir"] = library_dir
    hopla_env = add_auth_information_to_env(dict(hopla_env))

    return hopla_env


def execute_hopla_dot_shell():
    script_dirname = os.path.dirname(Path(__file__).resolve())
    cmd_entry = script_dirname + "/hopla.sh"
    hopla_env = create_hopla_env(script_dirname)
    cmdline_args = sys.argv[1:]
    log.debug(f"About to run cmd={cmd_entry} with args: {cmdline_args}")
    subprocess.run(args=[cmd_entry] + cmdline_args,
                   env=hopla_env)


if __name__ == "__main__":
    log.debug("start application")
    execute_hopla_dot_shell()
