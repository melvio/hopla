import logging
import click
import requests

from hopla.hoplalib.Http import RequestHeaders, UrlBuilder

log = logging.getLogger()


@click.group()
def api():
    pass


@api.command()
def content():
    log.debug("function: content")
    raise NotImplementedError("api content")


@api.command()
def version():
    log.debug("function: version")
    click.echo(UrlBuilder().api_version)


@api.command()
def status():
    log.debug("function: api")

    url_builder = UrlBuilder(path_extension="/status")
    headers = RequestHeaders().get_default_request_headers()
    response = requests.get(url=url_builder.url, headers=headers)

    click.echo(response.json())
