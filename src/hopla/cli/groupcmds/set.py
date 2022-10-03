"""
The module with CLI code that handles the `hopla set` group command.
"""
import logging

import click
import requests

from hopla.hoplalib.http import RequestHeaders, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.hoplalib.http import HabiticaRequest

log = logging.getLogger()


@click.group()
def set():  # pylint: disable=redefined-builtin
    """
    GROUP to set things in Habitica.
    """


@set.command()
@click.argument("day_start_hour", type=click.IntRange(min=0, max=23),
                default=0, metavar="[HOUR]")
@click.option("--json/--no-json", "json_flag",
              default=False, show_default=True,
              help="Output the command result in JSON.")
def day_start(day_start_hour, json_flag: bool):
    """Set your day-start (CRON) to the specified HOUR.

    HOUR - sets the day start to the N-th hour of the day. HOUR may range
    from 0 to 23 (inclusive). 0 AM (midnight) will be used as the
    default day start hour when no hour is specified.


    \b
    Examples:
    ---
    # Set the day start to 01:00 AM.
    $ hopla set day-start 1
    Your custom day start has changed.

    \b
    # Set the day start to 00:00 AM and get JSON output (e.g. for pipelines).
    $ hopla set day-start --json
    { "message": "Your custom day start has changed." }


    \f
    :param day_start_hour:
    :param json_flag
    """
    log.debug(f"hopla set day-start {day_start_hour}")

    headers = RequestHeaders().get_default_request_headers()
    body = {"dayStart": day_start_hour}
    url = UrlBuilder(path_extension="/user/custom-day-start").url

    response = requests.post(
        url=url,
        headers=headers,
        json=body,
        timeout=HabiticaRequest.TIMEOUT
    )

    json = response.json()
    json_data = json["data"]
    if json_flag:
        click.echo(JsonFormatter(json_data).format_with_double_quotes())
    else:
        click.echo(json_data["message"])
