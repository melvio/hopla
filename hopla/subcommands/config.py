#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import List
from configparser import ConfigParser

import click
import os

import logging

log = logging.getLogger()


class ConfigurationFile:
    """Hopla's configuration file"""

    def __init__(self):
        # TODO: we can probably use python-click to handle this for us
        self._global_env_var_xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        self._global_env_var_hopla_conf_file = os.environ.get("HOPLA_CONF_FILE")

    @property
    def file_path(self) -> Path:
        if self._global_env_var_hopla_conf_file is not None:
            config_file = Path(self._global_env_var_hopla_conf_file)
        elif self._global_env_var_xdg_config_home is not None:
            config_file = Path(self._global_env_var_xdg_config_home) / "hopla" / "hopla.conf"
        else:
            config_file = Path.home() / ".config" / "hopla" / "auth.conf"

        # TODO: check if resolve could fail if these dirs dont exist
        return config_file.resolve()

    @property
    def exists(self) -> bool:
        return self.file_path.exists() and self.file_path.is_file()

    def _create_empty_conf_file_if_it_doesnt_exists(self):
        with open(self.file_path, mode="a"):
            pass  # no need to write to it, just create it

    def _creat_conf_dir(self):
        Path.mkdir(self.file_path.parent, parents=True, exist_ok=True)


class InvalidConfigFile(Exception):
    """ Raised when hopla's config file is not use-able"""

    def __init__(self, message):
        self.message = message

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class ConfigurationFileParser:
    # TODO: really gotta handle this better.. have to much error checking going on.. functions
    #       are doing stuff they are not supposed to be doing
    def __init__(self, conf_file: Path = None):
        if conf_file is None:
            self._conf_file: Path = ConfigurationFile().file_path
        else:
            self._conf_file: Path = conf_file

        self.config_parser = ConfigParser()

        try:
            # TODO: facepalm error handling in constructor
            self._validate()
        except InvalidConfigFile:
            with open(self._conf_file, mode="w"):
                self.write_core_section_if_there_is_none()

    def _validate(self):
        if not self._conf_file.exists() or not self._conf_file.is_file():
            msg = f"config file {self._conf_file} does not exist or is not a file"
            log.debug(msg)
            raise InvalidConfigFile(msg)

        files = self.config_parser.read(self._conf_file)
        if len(files) != 1:
            msg = f"config file parser parsed an invalid amount of valid: files={files}"
            log.debug(msg)
            raise InvalidConfigFile(msg)

        if not self.config_parser.has_section("core"):
            msg = f"expected a core section but got sections={self.config_parser.sections()}"
            log.debug(msg)
            raise InvalidConfigFile(msg)

    def write_core_section_if_there_is_none(self):
        self.config_parser.read(self._conf_file)
        if not self.config_parser.has_section("core"):
            self.config_parser.add_section("core")
        # TODO: watch out: we lose all other config here too..
        #       make sure we have more solid setup later
        with open(self._conf_file, mode="w") as new_conf_file:
            self.config_parser.write(new_conf_file)

    # let's use 'core' section for now
    # TODO: better section management? Kinda like git config does
    def get_key_from_section(self, config_name, section="core"):
        self.config_parser.read(self._conf_file)
        if not self.config_parser.has_section(section):
            return f"section {section} not found in {self._conf_file}"
        if not self.config_parser.has_option(section=section, option=config_name):
            return f"config_name '{config_name}' not found in {self._conf_file}"
        return self.config_parser.get(section=section, option=config_name)

    # let's use core section for now
    # TODO: better section management? Kinda like git config does
    def set_key_in_section_to_value(self, config_name, config_value, section="core"):
        self.config_parser.read(self._conf_file)
        self.config_parser.set(
            section=section,
            option=config_name,
            value=config_value
        )
        with open(self._conf_file, mode="w") as updated_config_file:
            self.config_parser.write(updated_config_file)
        # return new value
        return config_value


def config_get(config_name: str):
    config_file_parser = ConfigurationFileParser()
    value = config_file_parser.get_key_from_section(config_name=config_name)
    click.echo(f"{value}")


def config_set(config_name: str, value):
    config_file_parser = ConfigurationFileParser()
    value = config_file_parser.set_key_in_section_to_value(config_name=config_name,
                                                           config_value=value)
    click.echo(f"{config_name}={value}")


def get_config_file_name():
    click.echo(ConfigurationFile().file_path)


def get_config_file_content():
    with open(ConfigurationFile().file_path, mode="r") as conf_file:
        for line in conf_file.readlines():
            click.echo(line.strip())


# TODO: actually use the value of debug_enabled in the logging framework
supported_config_names = click.Choice(["debug_enabled"])


@click.command()
@click.argument("config_name", required=False, type=supported_config_names)
@click.argument("value", required=False)
@click.option("--list", "show_config_file_content",
              is_flag=True, help="list the contents of the config file")
@click.option("--config-file-name", "show_config_file_name",
              is_flag=True, help="get the config file's absolute path")
# @click.argument("arguments", metavar="[config_name] [value]", nargs=-1)
def config(config_name: str, value,
           show_config_file_name_flag: bool,
           show_config_file_content_flag: bool):
    """get, set, or list config values

    Note that hopla config emulates git config in structure

    \b
    hopla config CONFIG_NAME        # get value of CONFIG_NAME
    hopla config CONFIG_NAME VALUE  # give CONFIG_NAME the specified VALUE
    hopla config --list             # show all config values

    \b
    Examples
    ---
    # turn debug_enabled to 1 (TODO: currently not yet supported)
    hopla config debug_enabled 1


    \f
    :param show_config_file_name_flag: whether to display the config file name
    :param show_config_file_content_flag: whether to display the config file name
    :param value:
    :param config_name:
    :return:
    """
    log.debug(f"hopla config name={config_name} value={value}")
    log.debug(f" options:  get_config_file_name={get_config_file_name}")

    # TODO: cleanup if else stuff
    if show_config_file_name_flag:
        get_config_file_name()
    elif show_config_file_content_flag:
        get_config_file_content()
    elif value is None:
        if config_name is None:
            click.echo(config.help)
        else:
            config_get(config_name=config_name)
    else:
        config_set(config_name, value)
