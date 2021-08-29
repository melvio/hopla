"""
The module with CLI code that handles the `hopla api` group command.
"""
import logging

import click
import jq
import requests

from hopla.hoplalib.clickhelper import data_on_success_else_exit
from hopla.hoplalib.http import UrlBuilder
from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


@click.group()
def api():
    """GROUP for requesting Habitica API metadata"""


@api.command()
@click.option("--jq-filter", "-j", metavar="JQ_FILTER",
              help="JQ_FILTER is a `jq` filter that can be used to restructure output")
def content(jq_filter: str) -> dict:
    """get detailed information about Habitica's API content

    \b
    Example
    ----
    # Tip: the content is pretty long so try piping it to an editor or pager
    hopla api content | vim -

    \b
    # get content information about
    # the [Ruby Rapport quest](https://habitica.fandom.com/wiki/Ruby_Rapport)
    hopla api content --jq-filter ".quests.ruby"


    [API-docs](https://habitica.com/apidoc/#api-Content-ContentGet)
    \f
    :return:
    """

    log.debug("hopla api content")

    url_builder = UrlBuilder(path_extension="/content")
    response = requests.get(url=url_builder.url)
    content_data: dict = data_on_success_else_exit(response)

    if jq_filter:
        user_requested_content_data = jq.compile(jq_filter).input(content_data).first()
    else:
        user_requested_content_data = content_data

    content_as_json: str = JsonFormatter(user_requested_content_data).format_with_double_quotes()
    click.echo(content_as_json)

    return content_data


valid_model_names = click.Choice(
    choices=["user", "group", "challenge", "tag", "habit", "daily", "todo", "reward"],
    case_sensitive=False
)


@api.command()
@click.argument("model_name", type=valid_model_names)
def model(model_name: str) -> dict:
    """returns the specified habitica API datamodel

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
    # headers = RequestHeaders().get_default_request_headers()

    response = requests.get(url=url_builder.url)
    model_data = data_on_success_else_exit(response)

    click.echo(JsonFormatter(model_data).format_with_double_quotes())
    return model_data


@api.command()
def version() -> str:
    """print the version string of the Habitica API (e.g. v3)

    \f
    :return The habitica API version string. (e.g. v3, v4)
    """
    log.debug("hopla api version")
    click.echo(GlobalConstants.HABITICA_API_VERSION)
    return GlobalConstants.HABITICA_API_VERSION  # .appVersion maybe also interesting?


@api.command()
def status() -> dict:
    """get the hopla API availability status


    \f
    :return: The api status (expected: "status": "up")
    """
    log.debug("hopla api status")

    url_builder = UrlBuilder(path_extension="/status")
    response = requests.get(url=url_builder.url)
    status_data = data_on_success_else_exit(response)

    click.echo(JsonFormatter(status_data).format_with_double_quotes())
    return status_data
