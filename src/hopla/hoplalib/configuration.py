"""
Library code to handle Hopla's configuration.
"""
import logging
from configparser import ConfigParser
from pathlib import Path
from typing import List
from collections import namedtuple

from hopla.hoplalib.errors import PrintableException
from hopla.hoplalib.common import get_configuration_dirpath, EnvironmentVariables

log = logging.getLogger()


class HoplaConfigurationFile:
    """Hopla's configuration file"""

    def __init__(self, *, alternative_file=None):
        self.__alternative_file = alternative_file
        self.__global_env_var_hopla_conf_file = EnvironmentVariables.HOPLA_CONF_FILE

    @property
    def file_path(self) -> Path:
        """Get the hopla configuration file as a Path"""
        if self.__alternative_file is not None:
            config_file: Path = Path(self.__alternative_file)
        elif self.__global_env_var_hopla_conf_file is not None:
            config_file: Path = Path(self.__global_env_var_hopla_conf_file)
        else:
            config_file: Path = get_configuration_dirpath() / "hopla.conf"

        return config_file.resolve()

    def exists(self) -> bool:
        """Return true if the hopla configuration file exists"""
        return self.file_path.exists() and self.file_path.is_file()


class ConfigurationFileParser:
    """Class that writes and reads from the Hopla configuration file"""

    def __init__(self):
        self._conf_file = HoplaConfigurationFile()
        self.config_parser = ConfigParser()

    def get_full_config_name(self, full_config_name: str, *, fallback=None):
        """takes a full_config_name and returns the corresponding value in the config file

        For example: `get_full_config_name("cmd_all.loglevel")` returns 'warning' if
        the hopla config file contains:
        \b
        [cmd_all]
        loglevel = warning


        \f
        :param fallback:
        :param full_config_name:
        :return:
        """

        self.config_parser.read(self._conf_file.file_path)
        configuration_setting = FullConfigurationNameStr(full_config_name_str=full_config_name)

        return self.config_parser.get(
            section=configuration_setting.section,
            option=configuration_setting.short_config_name,
            fallback=fallback
        )

    def set_full_config_name(self, full_config_name: str, new_value):
        """
        Given a fully qualified config name (such cmd_all.loglevel) and a value, this
        function sets the new_value and returns the new_value.
        """
        self.config_parser.read(self._conf_file.file_path)
        configuration_setting = FullConfigurationNameStr(full_config_name_str=full_config_name)

        self.config_parser.set(
            section=configuration_setting.section,
            option=configuration_setting.short_config_name,
            value=new_value
        )
        with open(self._conf_file.file_path, mode="w", encoding="utf-8") as updated_conf_file:
            self.config_parser.write(updated_conf_file)

        return new_value


class InvalidFullNameFormat(PrintableException):
    """An exception that is thrown when a configuration full name doesn't have the valid format"""


ConfigurationName = namedtuple(typename="ConfigurationNameType",
                               field_names=["section", "config_name"])


class FullConfigurationNameStr:
    """The full configuration name of format:
            ini_section_name.key_name

        the full name 'cmd_all.loglevel' maps to the following in a config file:
        [cmd_all]
        loglevel = ...
    """

    def __init__(self, full_config_name_str: str):
        try:
            split_name: List[str] = full_config_name_str.split(".")
            self.__section, self.__config_short_name = split_name
            self.__config_name = ConfigurationName(section=self.__section,
                                                   config_name=self.__config_short_name)
        except ValueError as ex:
            raise InvalidFullNameFormat(
                "Expected a full_config_name of format: 'ini_section_name.key_name'"
                f"but received {full_config_name_str}"
            ) from ex

    def __str__(self) -> str:
        return str(self.get_validated_config_name())

    def get_validated_config_name(self) -> ConfigurationName:
        """Return the underlying named tuple"""
        return self.__config_name

    @property
    def section(self) -> str:
        """Return the section part of the Full configuration name string"""
        return self.__section

    @property
    def short_config_name(self):
        """Return the (short) name part of the Full configuration name string"""
        return self.__config_short_name


class HoplaDefaultConfiguration:
    """
    A class responsible for keeping track of the supported configuration and the default values.
    """

    @property
    def default_config_as_parser(self) -> ConfigParser:
        """
        Returns a ConfigParser with the default configuration assuming that nobody
        ever configured anything.

        :return:
        """
        default_config = ConfigParser()
        # [cmd_all] # config for all command
        # [cmd_XXX] # config for command XXX
        all_commands_section = "cmd_all"
        default_config.add_section(all_commands_section)

        # debug: for developers (too much info)
        # info: for developers (basic info, incl. graceful degradation)
        # warning: something worth of creating an issue on github, but nothing broke
        # error: user experienced something breaking down
        default_config.set(all_commands_section, "loglevel", "warning")
        return default_config

    def supported_sections(self):
        """Return the sections that are supported in the Hopla Configuration file."""
        return self.default_config_as_parser.sections()


class ConfigInitializer:
    """Helper class for initializing Hopla's configuration files."""

    def __init__(self):
        self.config_file = HoplaConfigurationFile()

    def initialize_before_running_cmds(self) -> bool:
        """"
        Create the default config file if no config file exists.

        :return: True if a file was created, false else.
        """
        if self.config_file.exists() is False:
            self._create_empty_config_file()
            default_config = HoplaDefaultConfiguration().default_config_as_parser
            with open(self.config_file.file_path, mode="w", encoding="utf-8") as new_conf_file:
                default_config.write(new_conf_file)
            return True

        return False

    def _create_empty_config_file(self):
        Path.mkdir(self.config_file.file_path.parent, parents=True, exist_ok=True)
        with open(self.config_file.file_path, mode="w", encoding="utf-8"):
            pass  # no need to write to it, just create it
