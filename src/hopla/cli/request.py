"""
The module with CLI code that handles the `hopla request` command.
"""
import logging
from typing import Dict, List, Tuple

import click
import requests
from requests import PreparedRequest, Response, Request

from hopla.hoplalib.http import RequestHeaders
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()

BodyParam = Tuple[str, str]


@click.command()
@click.option(
    "--method", "-X", default="GET", show_default=True,
    type=click.Choice(["GET", "POST"]),
    help="The HTTP method."
)
@click.option(
    "--domain", default="https://habitica.com", show_default=True,
    metavar="URL",
    help="The domain name where the Habitica API is hosted."
)
@click.option(
    "--body-param", "body_param_list", multiple=True, type=click.Tuple([str, str]),
    metavar="{KEY} {VALUE}",
    default=[], show_default=False,
    help="A key-value pair for in the JSON body. E.g. --body-param 'dayStart' '0' ."
         "The --body-param option can be used multiple times."
)
@click.option(
    "--show-response-headers", "-I", "show_response_headers_flag",
    is_flag=True, default=False, show_default=True,
    help="Print the HTTP response headers to stdout."
)
@click.option(
    "--show-status-code", "show_status_code_flag",
    is_flag=True, default=False, show_default=True,
    help="Print the HTTP response code (e.g. 201) to stdout."
)
@click.option(
    "--show-response/--no-show-response", "show_response_flag",
    is_flag=True, default=True, show_default=True,
    help="Print the HTTP response body."
)
@click.argument("path")
def request(method: str,
            domain: str,
            body_param_list: List[BodyParam],
            show_response_headers_flag: bool,
            show_status_code_flag: bool,
            show_response_flag: bool,
            path: str):
    # pylint: disable=too-many-arguments
    """Perform a HTTP request on the Habitica API.

    PATH This is the path of the endpoint that you want to perform a HTTP
    request on. For example, /api/v3/groups.

    \b
    Examples
    ----
    # GET: get party information
    $ hopla request /api/v3/groups/party

    \b
    # GET: a user's tasks
    $ hopla request /api/v3/tasks/user

    \b
    # GET: a user's habits
    $ hopla request /api/v3/tasks/user?type=habits

    \b
    # POST: open a mystery item
    $ hopla request --method=POST /api/v3/user/open-mystery-item

    \b
    # POST: send a quest invite for Recidivate pt. 3 to your party
    $ hopla request --method POST /api/v3/groups/party/quests/invite/moonstone3

    \b
    # POST: buy a special item. In this case, a spooky sparkles item.
    $ hopla request -XPOST /api/v3/user/buy-special-spell/spookySparkles

    \b
    # POST: cast the Searing Brightness (Healer) and Tool of Trade (Rogue) spell.
    $ hopla request -XPOST /api/v3/user/class/cast/brightness
    $ hopla request -XPOST /api/v3/user/class/cast/toolsOfTrade

    \b
    # POST: set your custom day start to 1 AM
    $ hopla request -XPOST --body-param dayStart 1 /api/v3/user/custom-day-start


    \b
    # Only show the HTTP response headers
    $ hopla request /api/v3/user --show-response-headers --no-show-response

    \b
    # Only show the HTTP status code
    $ hopla request /api/v3/challenges/groups/party --show-status-code --no-show-response

    \b
    # Show headers, status code and response.
    $ hopla request /api/v3/challenges/groups/party --show-response-headers --show-status-code



    \f
    :return:
    """

    # There is no support for query parameters yet, however, you can use ?y=x in the
    # path to get around this.
    log.debug(f"hopla request {method} {domain=} {path=}\n"
              f"  {body_param_list=}\n"
              f"  {show_response_headers_flag=} {show_status_code_flag=}\n"
              f"  {show_response_flag=}")

    response: Response = perform_request(
        method=method,
        request_endpoint=f"{domain}{path}",
        body_params=dict(body_param_list)
    )

    display_response(
        response=response,
        show_response_headers=show_response_headers_flag,
        show_status_code=show_status_code_flag,
        show_response=show_response_flag,
    )


def perform_request(*, method: str,
                    request_endpoint: str,
                    body_params: Dict[str, str]) -> Response:
    """
    Create and execute an API request according to the specified parameters.

    :param method:
    :param request_endpoint:
    :param body_params:
    :return:
    """
    headers: dict = RequestHeaders().get_default_request_headers()

    http_request = Request(
        method=method,
        url=request_endpoint,
        headers=headers,
        json=body_params or None
    )
    prepared_request: PreparedRequest = http_request.prepare()
    return requests.session().send(prepared_request)


def display_response(response: Response, *,
                     show_response_headers: bool,
                     show_status_code: bool,
                     show_response: bool) -> None:
    """
    Display the requests.Response object in accordance to the specified flags.
    """
    if show_response_headers is True:
        click.echo("RESPONSE HEADERS")
        for header_name, header_value in response.headers.items():
            click.echo(f"{header_name}: {header_value}")

    if show_status_code is True:
        click.echo(f"HTTP Status Code: {response.status_code}")

    if show_response is True:
        # no support for non-JSON output
        click.echo(JsonFormatter(response.json()).format_with_double_quotes())
