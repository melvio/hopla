#!/usr/bin/env python3
"""
Module that constructs the CLI, handles configuration files initialization,
and sets up logging.
"""
import logging
import sys

import click

from hopla.cli.authenticate import authenticate
from hopla.cli.buy.enchanted_armoire import enchanted_armoire
from hopla.cli.cast import cast
from hopla.cli.complete import complete
from hopla.cli.config import config
from hopla.cli.feed import feed
from hopla.cli.feed_all import feed_all
from hopla.cli.get_group import get_group
from hopla.cli.get_user.auth import auth
from hopla.cli.get_user.info import info
from hopla.cli.get_user.inventory import inventory
from hopla.cli.get_user.stats import stats
from hopla.cli.groupcmds.add import add
from hopla.cli.groupcmds.api import api
from hopla.cli.groupcmds.buy import buy
from hopla.cli.groupcmds.get_user import get_user
from hopla.cli.groupcmds.set import set  # pylint: disable=redefined-builtin
from hopla.cli.request import request
from hopla.cli.support_development import support_development
from hopla.cli.version import version
from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.configuration import ConfigInitializer, ConfigurationFileParser
from hopla.hoplalib.hoplaversion import HoplaVersion


def setup_logging() -> logging.Logger:
    """Setup python logging for the entire hopla project"""

    parsed_loglevel = ConfigurationFileParser().get_full_config_name("cmd_all.loglevel",
                                                                     fallback="info")
    loglevel_mapping = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }

    # https://docs.python.org/3.8/howto/logging.html#logging-basic-tutorial
    logging.basicConfig(
        format="[%(levelname)s][%(filename)s|%(asctime)s] %(message)s",
        level=loglevel_mapping[parsed_loglevel],
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    return logging.getLogger(__name__)


log = setup_logging()
log.debug(f"start application with arguments: {sys.argv}")

HOPLA_CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],  # add -h
    auto_envvar_prefix=GlobalConstants.APPLICATION_NAME
)


@click.group(context_settings=HOPLA_CONTEXT_SETTINGS)
@click.version_option(version=HoplaVersion().semantic_version())
def hopla():
    """hopla - a command line interface (CLI) to interact with habitica.com"""


def organize_cli() -> None:
    """Attach the subgroups and subcommands to the top hopla group command"""
    # hopla subcommands
    hopla.add_command(cast)
    hopla.add_command(config)
    hopla.add_command(complete)
    hopla.add_command(version)
    hopla.add_command(authenticate)
    hopla.add_command(feed)
    hopla.add_command(feed_all)
    hopla.add_command(support_development)
    hopla.add_command(request)
    hopla.add_command(get_group)

    # hopla subgroups
    hopla.add_command(add)
    hopla.add_command(api)
    hopla.add_command(set)
    hopla.add_command(buy)
    hopla.add_command(get_user)

    # hopla buy subgroup
    buy.add_command(enchanted_armoire)

    # hopla get-user subgroup
    get_user.add_command(inventory)
    get_user.add_command(stats)
    get_user.add_command(info)
    get_user.add_command(auth)


def init_hopla_config_files() -> None:
    """Setup the config file."""
    had_to_create_new_config_file: bool = ConfigInitializer().initialize_before_running_cmds()
    if had_to_create_new_config_file:
        click.echo(f"Thank you for trying out {GlobalConstants.APPLICATION_NAME}")
        click.echo(
            "Bug reports, pull requests, and feature requests are welcomed over at:  "
        )
        click.echo(GlobalConstants.ISSUE_URL)


def kickstart_hopla() -> None:
    """Setup the config files, organize the CLI, and call the base command group."""
    init_hopla_config_files()
    organize_cli()
    hopla()
