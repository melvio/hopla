import logging

import click
import requests

from hopla.hoplalib.Http import RequestHeaders, UrlBuilder
from hopla.hoplalib.OutputFormatter import JsonFormatter

log = logging.getLogger()


@click.group()
def set():
    """GROUP to set things in Habitica"""
    pass


valid_day_start_hours = click.Choice([str(i) for i in range(0, 24)])


@set.command()
@click.argument("day_start_hour", type=valid_day_start_hours, default="0",
                metavar="[HOUR]")
@click.option("--json/--no-json", "json_flag", default=False, )
def day_start(day_start_hour, json_flag: bool):
    """Set your day-start (CRON) to the specified HOUR.

    HOUR - sets the day start to the N-th hour of the day. HOUR may range
    from 0 to 23 (inclusive). 0 AM (midnight) will be used as the
    default day start hour when no hour is specified.


    \b
    Examples:
    ---
    # set the day start to 01:00 AM
    $ hopla set day-start 1
    Your custom day start has changed.

    \b
    # set the day start to 00:00 AM and get json output (e.g. for pipelines)
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

    response = requests.post(url=url, headers=headers, json=body)

    json = response.json()
    json_data = json["data"]
    if json_flag:
        click.echo(JsonFormatter(json_data).format_with_double_quotes())
    else:
        click.echo(json_data["message"])
