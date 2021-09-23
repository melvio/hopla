"""
The module with CLI code that handles the `hopla request` command.
"""
import logging
from typing import List, Tuple, Optional

import click
import requests
from hopla.hoplalib.http import RequestHeaders
from hopla.hoplalib.outputformatter import JsonFormatter

supported_http_request_methods = click.Choice(["GET", "POST"])

log = logging.getLogger()

BodyParam = Tuple[str, str]


@click.command()
@click.option("--method", "-X", default="GET", show_default=True,
              type=supported_http_request_methods,
              help="The HTTP method.")
@click.option("--domain", default="https://habitica.com", show_default=True,
              metavar="URL",
              help="The domain name where the Habitica API is hosted.")
@click.option("--body-param", "body_param_list", multiple=True, type=click.Tuple([str, str]),
              metavar="KEY VALUE",
              help="A key-value pair for in the JSON body. E.g. --body-param 'dayStart' '0' ."
                   "The --body-param option can be used multiple times.")
@click.argument("path")
def request(method: str,
            domain: str,
            body_param_list: Optional[List[BodyParam]],
            path: str):
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
    # POST: cast the Searing Brightness spell
    $ hopla request -XPOST /api/v3/user/class/cast/brightness

    \b
    # POST: set your custom day start to 1 AM
    $ hopla request -XPOST --body-param dayStart 1 /api/v3/user/custom-day-start

    \f
    :return:
    """
    log.debug(f"hopla request {method} DOMAIN+PATH={domain + path}")
    log.debug(f"   body_param_list={body_param_list}")

    request_endpoint: str = domain + path
    headers: dict = RequestHeaders().get_default_request_headers()

    # no support for query parameters yet
    if body_param_list:
        http_request = requests.Request(method=method,
                                        url=request_endpoint,
                                        headers=headers,
                                        json=dict(body_param_list))
    else:
        http_request = requests.Request(method=method,
                                        url=request_endpoint,
                                        headers=headers)

    response: requests.Response = requests.session().send(http_request.prepare())

    log.debug(f"HTTP Status Code: {response.status_code}")
    # no support for non-JSON output
    click.echo(JsonFormatter(response.json()).format_with_double_quotes())
