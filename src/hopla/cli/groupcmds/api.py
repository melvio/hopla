"""
The module with CLI code that handles the `hopla api` group command.
"""
import logging

import click
import requests

from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


@click.group()
def api():
    """GROUP for requesting Habitica API metadata."""


class ApiContentRequest:
    """Class that requests a user model from the Habitica API"""

    def __init__(self):
        self.url = UrlBuilder(path_extension="/content").url

    def request_api_content(self) -> requests.Response:
        """Perform the get API content request and return the response"""
        return requests.get(url=self.url, timeout=HabiticaRequest.TIMEOUT)

    def request_api_content_on_fail_exit(self) -> dict:
        """
        Function that requests the habitica API content.
        If the request was successful return the content, else exits.
        """
        api_response: requests.Response = self.request_api_content()
        return get_data_or_exit(api_response)


@api.command()
def content() -> dict:
    """Print detailed information about Habitica's API content.

    \b
    Example
    ----
    # Tip: The content is long, you can try piping it to an editor or pager.
    $ hopla api content | vim -
    $ hopla api content | less -

    \b
    # get content information about
    # the [Ruby Rapport quest](https://habitica.fandom.com/wiki/Ruby_Rapport)
    $ hopla api content | jq ".quests.ruby"


    [API-docs](https://habitica.com/apidoc/#api-Content-ContentGet)
    \f
    :return:
    """
    log.debug("hopla api content")

    content_data: dict = ApiContentRequest().request_api_content_on_fail_exit()
    content_as_json: str = JsonFormatter(content_data).format_with_double_quotes()
    click.echo(content_as_json)
    return content_data


valid_model_names = click.Choice(
    choices=["user", "group", "challenge", "tag", "habit", "daily", "todo", "reward"],
    case_sensitive=False
)


@api.command()
@click.argument("model_name", type=valid_model_names)
def model(model_name: str) -> dict:
    """Print the specified Habitica API datamodel.

    \b
    Example:
    ---
    # Get the 'group' datamodel
    $ hopla api model group

    [apidocs](https://habitica.com/apidoc/#api-Meta-GetUserModelPaths)

    \f
    :param model_name: The particular data model
    :return:
    """
    log.debug(f"hopla api model name={model_name}")

    url_builder = UrlBuilder(path_extension=f"/models/{model_name}/paths")
    response = requests.get(
        url=url_builder.url,
        timeout=HabiticaRequest.TIMEOUT
    )
    model_data = get_data_or_exit(response)

    click.echo(JsonFormatter(model_data).format_with_double_quotes())
    return model_data


@api.command()
def version() -> dict:
    """print the version string of the Habitica API (e.g. v3)

    \f
    :return The habitica API version string. (e.g. v3, v4)
    """
    log.debug("hopla api version")
    api_version = {"version": GlobalConstants.HABITICA_API_VERSION}
    click.echo(JsonFormatter(api_version).format_with_double_quotes())
    return api_version  # .appVersion maybe also interesting?


@api.command()
def status() -> dict:
    """Print the Habitica API availability status.


    \f
    :return: The API status (expected: "status": "up")
    """
    log.debug("hopla api status")

    url = UrlBuilder(path_extension="/status").url
    response = requests.get(url=url, timeout=HabiticaRequest.TIMEOUT)
    status_data = get_data_or_exit(response)

    click.echo(JsonFormatter(status_data).format_with_double_quotes())
    return status_data
