"""
The module with CLI code that handles the `hopla version` command.
"""

import logging

import click

log = logging.getLogger()

MAJOR_VERSION = 0
MINOR_VERSION = 0
PATCH_VERSION = 13
PRE_RELEASE = "alpha"


def hopla_version() -> str:
    """
    Prints the hopla version (Not to be confused with the habitica API version)

    The output should satisfy [semantic versioning](https://semver.org/)
    TODO: verify if this is the case
    """

    version_core = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
    if PRE_RELEASE is not None and PRE_RELEASE != "":
        pre_release = f"-{PRE_RELEASE}"
    else:
        pre_release = ""

    return version_core + pre_release


@click.command()
def version():
    """Print the Hopla version string.

    \f
    :return:
    """
    log.debug("hopla version")
    click.echo(hopla_version())
