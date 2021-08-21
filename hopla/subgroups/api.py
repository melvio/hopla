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
def model():
    log.debug("function: model")
    raise NotImplementedError("api model")


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
