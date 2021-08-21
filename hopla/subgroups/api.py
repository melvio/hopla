import logging
import click

from hopla.hoplalib.Http import RequestHeaders, UrlBuilder

log = logging.getLogger()


@click.group()
def api():
    pass


@api.command()
def version():
    log.debug("function: version")
    click.echo(UrlBuilder().api_version)


@api.command()
def content():
    log.debug("function: content")
    pass
