import logging
import click
import requests

from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

log = logging.getLogger()


@click.group()
def set():
    pass


valid_day_start_hours = click.Choice([str(i) for i in range(0, 24)])


@set.command()
@click.argument("day_start_hour", type=valid_day_start_hours, default="0")
def day_start(day_start_hour):
    log.debug(f"hopla set day-start {day_start_hour}")

    headers = RequestHeaders().get_default_request_headers()
    body = {"dayStart": day_start_hour}
    url = UrlBuilder(path_extension="/user/custom-day-start").url

    response = requests.post(url=url, headers=headers, json=body)

    # TODO: (contact:melvio) --json vs. user friendly output
    json = response.json()
    click.echo(json["data"]["message"])
