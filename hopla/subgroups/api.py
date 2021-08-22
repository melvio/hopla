import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def api():
    """ hopla api - command group for requesting the habitica API metadata

    :return:
    """
    pass


@api.command()
def content() -> str:
    """- Returns the content of habitica

    "content" as in content distribution network

    :return:
    """

    log.debug("function: content")

    url_builder = UrlBuilder(path_extension="/content")
    response = requests.get(url=url_builder.url)

    # TODO: add --json argument to enable json output
    text = response.text
    click.echo(text)
    return text


# todo: maybe get this dynamically from the API?
valid_model_names = ["user", "group", "challenge", "tag", "habit", "daily", "todo", "reward"]


@api.command()
@click.argument("model_name", type=click.Choice(valid_model_names, case_sensitive=False))
def model(model_name: str):
    """hopla api model - returns the specified habitica API datamodel

    :param model_name: The particular data model
    :return:
    """
    log.debug("function: model")

    url_builder = UrlBuilder(path_extension=f"/models/{model_name}/paths")
    # headers = RequestHeaders().get_default_request_headers()

    response = requests.get(url=url_builder.url)

    text = response.text
    click.echo(text)
    return text


@api.command()
def version() -> str:
    """
    hopla api version - returns the version string of the habitica.com API

    :return The habitica API version string. (e.g. v3, v4)
    """
    log.debug("function: version")
    api_version = UrlBuilder().api_version
    click.echo(api_version)
    return api_version


@api.command()
def status() -> str:
    """ hopla api status

    Returns the hopla API status

    :return: The api status (expected: "status": "up")
    """
    log.debug("function: api")

    url_builder = UrlBuilder(path_extension="/status")
    response = requests.get(url=url_builder.url)

    # TODO: add --json argument to enable json output
    text = response.text
    click.echo(text)
    return text
