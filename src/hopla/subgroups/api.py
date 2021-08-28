import logging
import click
import requests
import jq

from hopla.hoplalib.Http import UrlBuilder
from hopla.hoplalib.ClickUtils import data_on_success_else_exit
from hopla.hoplalib.OutputFormatter import JsonFormatter

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def api():
    """GROUP for requesting Habitica API metadata"""
    pass


@api.command()
@click.option("--jq-filter", "-j", metavar="JQ_FILTER", help="JQ_FILTER is a `jq` filter that can be used to restructure output")
def content(jq_filter: str) -> dict:
    """get habitica content


    \b
    Example
    ----
    # get information on the 'Ruby Rapport' quest
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
    click.echo(JsonFormatter(user_requested_content_data).format_with_double_quotes())
    return content_data


# todo: maybe get this dynamically from the API?
valid_model_names = click.Choice(["user", "group", "challenge", "tag", "habit", "daily", "todo", "reward"],
                                 case_sensitive=False)


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
    log.debug("hopla version")
    api_version = UrlBuilder().api_version
    click.echo(api_version)
    return api_version  # .appVersion maybe also interesting?


@api.command()
def status() -> dict:
    """get the hopla API availability status


    \f
    :return: The api status (expected: "status": "up")
    """
    log.debug("function: api")

    url_builder = UrlBuilder(path_extension="/status")
    response = requests.get(url=url_builder.url)
    status_data = data_on_success_else_exit(response)

    # TODO: add --json argument to enable json output
    click.echo(JsonFormatter(status_data).format_with_double_quotes())
    return status_data
