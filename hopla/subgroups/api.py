import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def api():
    """GROUP for requesting Habitica API metadata"""
    pass


@api.command()
def content() -> str:
    """print habitica content

    "content" as in content distribution network

    \f
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
valid_model_names = click.Choice(["user", "group", "challenge", "tag", "habit", "daily", "todo", "reward"],
                                 case_sensitive=False)


@api.command()
@click.argument("model_name", type=valid_model_names)
def model(model_name: str):
    """returns the specified habitica API datamodel

    \f
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
    """print the version string of the Habitica API (e.g. v3)

    \f
    :return The habitica API version string. (e.g. v3, v4)
    """
    log.debug("function: version")
    api_version = UrlBuilder().api_version
    click.echo(api_version)
    return api_version


@api.command()
def status() -> str:
    """get the hopla API availability status


    \f
    :return: The api status (expected: "status": "up")
    """
    log.debug("function: api")

    url_builder = UrlBuilder(path_extension="/status")
    response = requests.get(url=url_builder.url)

    # TODO: add --json argument to enable json output
    text = response.text
    click.echo(text)
    return text
