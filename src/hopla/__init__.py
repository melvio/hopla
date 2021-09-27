"""
Module responsible for setting up initialization of the hopla entry command.
"""
import sys

from hopla.kickstart import hopla, init_config, organize_cli, setup_logging
from hopla.hoplalib.configuration import ConfigurationFileParser

log = setup_logging()


def setup_hopla_cli():
    """The entry function for the hopla command"""
    init_config()
    log.debug(f"start application with arguments: {sys.argv}")
    organize_cli()
    hopla()
