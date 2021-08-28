import logging
import sys

import click

from hopla.hoplalib.Configuration import ConfigInitializer, ConfigurationFileParser
from hopla.cli.auth import auth
from hopla.cli.complete import complete
from hopla.cli.config import config
from hopla.cli.feed import feed
from hopla.cli.version import version
from hopla.cli.groupcmds.add import add
from hopla.cli.groupcmds.api import api
from hopla.cli.groupcmds.buy import buy
from hopla.cli.groupcmds.get import get
from hopla.cli.groupcmds.set import set


def setup_logging() -> logging.Logger:
    """Setup python logging for the entire hopla project"""
    parsed_loglevel = ConfigurationFileParser().get_full_config_name("cmd_all.loglevel")
    # TODO: move mapping to config itself.. logging should not be responsible for this
    loglevel_mapping = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }

    # https://docs.python.org/3.8/howto/logging.html#logging-basic-tutorial
    logging.basicConfig(
        format='[%(levelname)s][%(filename)s|%(asctime)s] %(message)s',
        level=loglevel_mapping[parsed_loglevel],
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    return logging.getLogger(__name__)


log = setup_logging()


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def hopla():
    """hopla - a command line interface (CLI) to interact with habitica.com"""
    pass


def entry_cmd():
    had_to_create_new_config_file = ConfigInitializer().initialize_before_running_cmds()
    if had_to_create_new_config_file:
        click.echo("Thank you for trying out hopla in its early release")
        click.echo("Bug reports, pull requests, and feature requests are welcomed over at:  ")
        click.echo("  <https://github.com/melvio/hopla>")
    log.debug(f"start application with arguments: {sys.argv}")
    # subgroups
    hopla.add_command(add)
    hopla.add_command(api)
    hopla.add_command(set)
    hopla.add_command(buy)
    hopla.add_command(get)
    # subcommands
    hopla.add_command(config)
    hopla.add_command(complete)
    hopla.add_command(version)
    hopla.add_command(auth)
    hopla.add_command(feed)
    hopla()
