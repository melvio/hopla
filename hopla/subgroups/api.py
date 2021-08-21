import logging
import click
import requests

from hopla.hoplalib.Http import RequestHeaders, UrlBuilder

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
    click.echo(response.json())


@api.command()
@click.argument("model_name")
def model(model_name: str):
    log.debug("function: model")

    url_builder = UrlBuilder(path_extension=f"/models/{model_name}/paths")
    # headers = RequestHeaders().get_default_request_headers()

    response = requests.get(url=url_builder.url)

    click.echo(response.json())


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
    click.echo(response.json())
