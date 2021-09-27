"""
The module with CLI code that handles the `hopla config` command.
"""

import logging
from pathlib import Path

import click

from hopla.hoplalib.configuration import ConfigurationFileParser
from hopla.hoplalib.configuration import HoplaConfigurationFile

log = logging.getLogger()


def config_get(config_name: str):
    """Get the value of the specified full configuration name"""
    if config_name is None:
        click.echo(config.help)
    else:
        config_file_parser = ConfigurationFileParser()
        value = config_file_parser.get_full_config_name(full_config_name=config_name)
        click.echo(f"{value}")


def config_set(config_name: str, value):
    """Set the value of the specified full configuration name"""
    config_file_parser = ConfigurationFileParser()
    value = config_file_parser.set_full_config_name(full_config_name=config_name,
                                                    new_value=value)
    click.echo(f"{config_name}={value}")


def print_config_file_name():
    """
    Prints the path of the configuration file that this `hopla config ...` invocation uses.
    """
    click.echo(HoplaConfigurationFile().file_path)


def print_config_file_content():
    """Print the hopla config file's content."""
    config_file_path: Path = HoplaConfigurationFile().file_path
    with open(config_file_path, mode="r", encoding="utf-8") as conf_file:
        for line in conf_file.readlines():
            click.echo(line.strip())


supported_config_names = click.Choice(["cmd_all.loglevel"])
"""Values supported: debug,info,warning,error"""


@click.command()
@click.argument("config_name", required=False, type=supported_config_names)
@click.argument("value", required=False)
@click.option("--list/--no-flag", "list_flag",
              default=False, show_default=True,
              help="List the contents of the config file.")
@click.option("--config-file-name/--no-config-file-name", "config_file_name_flag",
              default=False, show_default=True,
              help="Get the absolute path of the config file.")
def config(config_name: str,
           value,
           list_flag: bool,
           config_file_name_flag: bool):
    """Get, set, or list config values.

    Note that hopla config emulates git config in structure

    \b
    hopla config CONFIG_NAME        # get value of CONFIG_NAME
    hopla config CONFIG_NAME VALUE  # give CONFIG_NAME the specified VALUE
    hopla config --list             # show all config values

    \b
    Examples
    ---
    # get logging level
    $ hopla config cmd_all.loglevel
    warning

    \b
    # set logging level to info
    $ hopla config cmd_all.loglevel info
    cmd_all.loglevel=info

    \b
    # list the configuration values
    $ hopla config --list

    \b
    # display the config file path
    $ hopla config --config-file-name


    \f
    :param list_flag: whether to display the config file name
    :param config_file_name_flag: whether to display the config file name
    :param value:
    :param config_name:
    :return:
    """
    log.debug(f"hopla config name={config_name} value={value}")
    log.debug(f" options: --list={list_flag} --config_file_name={config_file_name_flag}")

    if list_flag:
        print_config_file_content()
    elif config_file_name_flag:
        print_config_file_name()
    elif value is None:
        config_get(config_name)
    else:
        config_set(config_name, value)
