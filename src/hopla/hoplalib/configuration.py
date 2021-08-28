"""
Library code to handle Hopla's configuration.
"""
import logging
import os
from configparser import ConfigParser
from pathlib import Path

log = logging.getLogger()


class HoplaConfigurationFile:
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
            config_file = Path.home() / ".config" / "hopla" / "hopla.conf"

        # TODO: check if resolve could fail if these dirs dont exist
        return config_file.resolve()

    @property
    def exists(self) -> bool:
        """Return true if the hopla configuration file exists"""
        return self.file_path.exists() and self.file_path.is_file()


class ConfigurationFileParser:
    def __init__(self):
        self._conf_file: Path = HoplaConfigurationFile().file_path

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

        self.config_parser.read(self._conf_file)
        section_name = FullConfigurationName(full_config_name=full_config_name).section
        config_name = FullConfigurationName(full_config_name=full_config_name).config_name

        return self.config_parser.get(
            section=section_name,
            option=config_name,
            fallback=fallback
        )

    def set_full_config_name(self, full_config_name: str, new_value):
        self.config_parser.read(self._conf_file)

        section_name = FullConfigurationName(full_config_name=full_config_name).section
        config_name = FullConfigurationName(full_config_name=full_config_name).config_name

        self.config_parser.set(
            section=section_name,
            option=config_name,
            value=new_value
        )
        with open(self._conf_file, mode="w", encoding="utf-8") as updated_conf_file:
            self.config_parser.write(updated_conf_file)

        return new_value


class FullConfigurationName:
    def __init__(self, full_config_name: str):
        """
           config_name format:
                ini_section_name.key_name

            so cmd_all.loglevel maps to:
            [cmd_all]
            loglevel = ...
        """
        self.full_config_name = full_config_name

    def __str__(self) -> str:
        return self.__class__.__name__ + f"(section={self.section}, config_name={self.config_name})"

    def _split_config_name(self):
        result = self.full_config_name.split(".")
        if len(result) != 2:
            raise ValueError(f"config_name={self.full_config_name} has an invalid format")
        # TODO: upgrade to named tuple
        return result[0], result[1]

    @property
    def section(self):
        return self._split_config_name()[0]

    @property
    def config_name(self):
        return self._split_config_name()[1]


class HoplaConfiguration:
    @property
    def default_config(self) -> ConfigParser:
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
        return self.default_config.sections()


class ConfigInitializer:
    """Helper class for initializing Hopla's configuration files."""

    def __init__(self):
        self.config_file = HoplaConfigurationFile()

    def initialize_before_running_cmds(self) -> bool:
        """"
        Create the default config file if no config file exists.

        :return: True if a file was created, false else.
        """
        if self.config_file.exists is False:
            self._create_empty_config_file()
            default_config = HoplaConfiguration().default_config
            with open(self.config_file.file_path, mode="w", encoding="utf-8") as new_conf_file:
                default_config.write(new_conf_file)
            return True

        return False

    def _create_empty_config_file(self):
        Path.mkdir(self.config_file.file_path.parent, parents=True, exist_ok=True)
        with open(self.config_file.file_path, mode="w", encoding="utf-8"):
            pass  # no need to write to it, just create it
