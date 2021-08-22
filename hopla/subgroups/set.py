import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


@click.group()
def set():
    """GROUP to set things in Habitica"""
    pass


valid_day_start_hours = click.Choice([str(i) for i in range(0, 24)])


@set.command()
@click.argument("day_start_hour", type=valid_day_start_hours, default="0", metavar="[HOUR]")
def day_start(day_start_hour):
    """Set your day-start (CRON) to the specified HOUR

    HOUR - sets the day start to the N-th hour of the day. HOUR may range
    from 0 to 23 (inclusive). 0 AM (midnight) will be used as the
    default day start hour when no hour is specified.


    \b
    Examples:
    ---
    # set the day start to 01:00 AM
    $ hopla set day-start 1

    \b
    # set the day start to 00:00 AM
    $ hopla set day-start





    """
    log.debug(f"hopla set day-start {day_start_hour}")

    headers = RequestHeaders().get_default_request_headers()
    body = {"dayStart": day_start_hour}
    url = UrlBuilder(path_extension="/user/custom-day-start").url

    response = requests.post(url=url, headers=headers, json=body)

    # TODO: (contact:melvio) --json vs. user friendly output
    json = response.json()
    click.echo(json["data"]["message"])
