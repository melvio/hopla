"""
Module with some Hopla common logic and data
"""
from typing import Final
from pathlib import Path
import os
import click


class GlobalConstants:
    """Class of global variables to be used by the entire application.

    Note that some of these constant may be upgraded to configuration parameters.
    """
    HABITICA_API_VERSION: Final[str] = "v3"
    """Version of the habitica API"""

    API_DOMAIN: Final[str] = "https://habitica.com"
    """Domain that provides the API """

    DEVELOPMENT_UUID: Final[str] = "79551d98-31e9-42b4-b7fa-9d89b0944319"
    """UUID of developer"""

    APPLICATION_NAME: Final[str] = "hopla"
    """Name of this application """

    X_CLIENT: Final[str] = f"{DEVELOPMENT_UUID}-{APPLICATION_NAME}"
    """
    BodyParam value used by hopla to identify itself to
    the habitica API <https://habitica.fandom.com/wiki/Guidance_for_Comrades>
    """

    SOURCE_CODE_REPOSITORY_URL: Final[str] = "https://github.com/melvio/hopla"
    """Repository for Hopla code"""

    ISSUE_URL: Final[str] = f"{SOURCE_CODE_REPOSITORY_URL}/issues"
    """Link which shows you an overview of the issues."""

    NEW_ISSUE_URL: Final[str] = f"{ISSUE_URL}/new"
    """Link which enables you to raise a new issue, suggest features, etc."""


class EnvironmentVariables:
    """Class with environment variables"""
    GLOBAL_ENV_VAR_HOPLA_AUTH_FILE: Final[str] = "HOPLA_AUTH_FILE"
    """ environment variable that a user can set to overwrite the
        default authenticate file """

    HOPLA_AUTH_FILE = os.environ.get(GLOBAL_ENV_VAR_HOPLA_AUTH_FILE)

    GLOBAL_ENV_VAR_HOPLA_CONF_FILE = "HOPLA_CONF_FILE"
    """ environment variable that a user can set to overwrite the
        default config file """

    HOPLA_CONF_FILE = os.environ.get(GLOBAL_ENV_VAR_HOPLA_CONF_FILE)


def get_configuration_dirpath() -> Path:
    """
    Get the most appropriate location for configuration (this is different per OS/environment)
    """
    return Path(click.get_app_dir(GlobalConstants.APPLICATION_NAME)).resolve()
