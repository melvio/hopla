#!/usr/bin/env python3

import click

import logging

from hopla.hoplalib.Configuration import ConfigurationFileParser, HoplaConfigurationFile

log = logging.getLogger()


def config_get(config_name):
    if config_name is None:
        click.echo(config.help)
    else:
        config_file_parser = ConfigurationFileParser()
        value = config_file_parser.get_full_config_name(full_config_name=config_name)
        click.echo(f"{value}")


def config_set(config_name: str, value):
    config_file_parser = ConfigurationFileParser()
    value = config_file_parser.set_full_config_name(full_config_name=config_name,
                                                    new_value=value)
    click.echo(f"{config_name}={value}")


def print_config_file_name():
    click.echo(HoplaConfigurationFile().file_path)


def print_config_file_content():
    with open(HoplaConfigurationFile().file_path, mode="r") as conf_file:
        for line in conf_file.readlines():
            click.echo(line.strip())


# TODO: get this value from the HoplaConfiguration class instead of duplicating it here
supported_config_names = click.Choice(["cmd_all.loglevel"])
# levels supported:
# hopla config cmd_all.loglevel debug
# hopla config cmd_all.loglevel info
# hopla config cmd_all.loglevel warning
# hopla config cmd_all.loglevel error



@click.command()
@click.argument("config_name", required=False, type=supported_config_names)
@click.argument("value", required=False)
@click.option("--list", "list_flag",
              is_flag=True,
              help="list the contents of the config file")
@click.option("--config-file-name", "config_file_name_flag",
              is_flag=True,
              help="get the absolute path of the config file")
# @click.argument("arguments", metavar="[config_name] [value]", nargs=-1)
def config(config_name: str,
           value,
           list_flag: bool,
           config_file_name_flag: bool):
    """get, set, or list config values

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


    \f
    :param list_flag: whether to display the config file name
    :param config_file_name_flag: whether to display the config file name
    :param value:
    :param config_name:
    :return:
    """
    log.debug(f"hopla config name={config_name} value={value}")
    log.debug(f" options:  list={list_flag}, config_file_name={config_file_name_flag}")

    if list_flag:
        print_config_file_content()
    elif config_file_name_flag:
        print_config_file_name()
    elif value is None:
        config_get(config_name)
    else:
        config_set(config_name, value)
