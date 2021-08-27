#!/usr/bin/env python3
import click

import logging

log = logging.getLogger()

MAJOR_VERSION = 0
MINOR_VERSION = 0
PATCH_VERSION = 1
PRE_RELEASE = "alpha"


def hopla_version() -> str:
    # <https://semver.org/>

    version_core = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
    if PRE_RELEASE is not None and PRE_RELEASE != "":
        pre_release = f"-{PRE_RELEASE}"
    else:
        pre_release = ""

    return version_core + pre_release


@click.command()
def version():
    """print hopla's version string

    \f
    :return:
    """
    log.debug("function: hopla version")
    click.echo(hopla_version())
