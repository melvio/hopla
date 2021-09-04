"""
The module with CLI code that handles the `hopla request` command.
"""
import logging
import click
import requests
from hopla.hoplalib.http import RequestHeaders
from hopla.hoplalib.outputformatter import JsonFormatter

supported_http_request_methods = click.Choice(["GET", "POST"])

log = logging.getLogger()


@click.command()
@click.option("--method", default="GET", show_default=True,
              type=supported_http_request_methods,
              help="The HTTP method")
@click.option("--domain", default="https://habitica.com", show_default=True,
              metavar="URL", type=str,
              help="The domain name where the Habitica API is hosted.")
@click.argument("path")
def request(method, domain: str, path: str):
    """Directly perform a HTTP request on the Habitica API

    PATH This is the path of the endpoint that you want to perform a HTTP
    request on. For example, /api/v3/groups.

    \b
    Examples
    ----
    # get a your party information
    $ hopla request /api/v3/groups/party

    \f
    :return:
    """
    log.debug(f"hopla request {method} DOMAIN+PATH={domain + path}")

    request_endpoint = domain + path
    headers: dict = RequestHeaders().get_default_request_headers()

    # no support for body and query parameters yet
    http_request = requests.Request(method=method,
                                    url=request_endpoint,
                                    headers=headers)
    response: requests.Response = requests.session().send(http_request.prepare())

    click.echo(f"HTTP Status Code: {response.status_code}")
    # no support for non-JSON output
    click.echo(JsonFormatter(response.json()).format_with_double_quotes())
