import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder

log = logging.getLogger()


# TODO: add some kind of json filtering
@click.group()
def api():
    pass


@api.command()
def content():
    log.debug("function: content")

    url_builder = UrlBuilder(path_extension="/content")
    response = requests.get(url=url_builder.url)

    # TODO: add --json argument to enable json output
    click.echo(response.text)


# todo: maybe get this dynamically from the API?
valid_model_names = ["user", "group", "challenge", "tag", "habit", "daily", "todo", "reward"]


@api.command()
@click.argument("model_name", type=click.Choice(valid_model_names, case_sensitive=False))
def model(model_name: str):
    log.debug("function: model")

    url_builder = UrlBuilder(path_extension=f"/models/{model_name}/paths")
    # headers = RequestHeaders().get_default_request_headers()

    response = requests.get(url=url_builder.url)

    click.echo(response.text)


@api.command()
def version():
    log.debug("function: version")
    click.echo(UrlBuilder().api_version)


@api.command()
def status():
    log.debug("function: api")

    url_builder = UrlBuilder(path_extension="/status")
    response = requests.get(url=url_builder.url)

    # TODO: add --json argument to enable json output
    click.echo(response.text)
