#!/usr/bin/env python3

import sys
import click
import os
import logging
from pathlib import Path
from argparse import ArgumentParser

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


from hopla.api.version import api


@click.group()
def hopla():
    pass


if __name__ == "__main__":
    log.debug(f"start application with arguments: {sys.argv}")
    script_dirname = os.path.dirname(Path(__file__).resolve())
    hopla_env = HoplaEnvironment().create_hopla_env(script_dirname=script_dirname)
    hopla.add_command(api)
    hopla()

#
# class GlobalOptionCmdLineParser:
#     def __init__(self, *, cmdline_args: List[str]):
#         self.cmdline_args = cmdline_args
#         self._help_option_enabled = False
#
#         # parse on init
#         self._parse_global_options()
#
#     def __str__(self) -> str:
#         return GlobalOptionCmdLineParser.__name__
#
#     # TODO: upgrade to argparser later on
#     def _parse_global_options(self):
#         for argument in self.cmdline_args:
#             longhelp = "--help"
#             shorthelp = "-h"
#             if argument == longhelp:
#                 self._help_option_enabled = True
#                 self.cmdline_args.remove(longhelp)
#             elif argument == shorthelp:
#                 self._help_option_enabled = True
#                 self.cmdline_args.remove(shorthelp)
#
#     @property
#     def help_option_enabled(self):
#         return self._help_option_enabled


# class HelpHandler:
#     # TODO: remove implicit assumption that --help is the only kind
#     def __init__(self, *, cmdline_args: List[str]):
#         self.cmdline_args = cmdline_args
#
#     def print_help_for_given_cmdline_args(self):
#         script_dirname: Path = Path(__file__).resolve().parent
#         cmds_dirname: Path = script_dirname / 'hopla'
#
#         # TODO handle implicit assumption that only 2 subcmds exist
#         if self.first_arg is not None:
#             possible_subcmd: Path = cmds_dirname / self.first_arg
#             if (possible_subcmd / ".py").is_file() or (possible_subcmd / ".sh").is_file():
#                 help_file = possible_subcmd / ".help"
#                 assert help_file.is_file(), "expected help to exist"
#                 # found help request
#                 subprocess.call(["cat", str(help_file)])
#                 exit(0)
#
#     @property
#     def first_arg(self):
#         try:
#             return self.cmdline_args[0]
#         except IndexError:
#             return None
#
#     @property
#     def second_arg(self):
#         try:
#             return self.cmdline_args[2]
#         except IndexError:
#             return None
#
