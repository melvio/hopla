"""
The module with CLI code that handles the `hopla get-group command.
"""

import logging
from typing import Optional

import click
import requests

from hopla.hoplalib.http import HabiticaRequest, UrlBuilder
from hopla.hoplalib.requests_helper import get_data_or_exit
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


class HabiticaGroupRequest(HabiticaRequest):
    """An API request object for getting group information.

    Related URLs:
    [wiki on groups](https://habitica.fandom.com/wiki/Groups)
    [apidoc on groups](https://habitica.com/apidoc/#api-Group)
    """

    def __init__(self, group_id: Optional[str] = "party"):
        # "party" is the magic string that identifies your current party.
        self.group_id = group_id

    @property
    def path(self) -> str:
        """Get the path for the url"""
        return f"/groups/{self.group_id}"

    @property
    def url(self) -> str:
        """Get the path for the url"""
        return UrlBuilder(path_extension=self.path).url

    def get_group_request(self) -> requests.Response:
        """Perform a GET request to get a group information."""
        return requests.get(
            url=self.url,
            headers=self.default_headers,
            timeout=HabiticaRequest.TIMEOUT
        )

    def get_group_data_or_exit(self) -> dict:
        """Get the group data or exit if the API request failed."""
        return get_data_or_exit(self.get_group_request())


@click.command()
@click.argument("group_id", default="party")
def get_group(group_id: str):
    """Get party information.

    GROUP_ID is the uuid of the group. When omitted your party information will be returned.

    \b
    Example
    ----
    # Get your party information:
    $ hopla get-group
    $ hopla get-group party

    \b
    # Get quest information
    $ hopla get-group | jq .quest

    \b
    # keep track of quest progress every 60 seconds
    $ watch --differences=permanent -n 60 'hopla get-group | jq .quest'

    \b
    # Get tavern information
    $ hopla get-group tavern

    \b
    # Specify a group by id
    $ hopla get-group 6fe49760-087f-4b08-9432-86fe77c2f1ef

    """
    log.debug(f"hopla get-party {group_id=}")

    group_request = HabiticaGroupRequest(group_id=group_id)
    group_info = group_request.get_group_data_or_exit()

    click.echo(JsonFormatter(group_info).format_with_double_quotes())
    return group_info
