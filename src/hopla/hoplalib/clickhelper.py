"""
Module with commonly used python-click functionality.
"""
import logging
import sys
import datetime
from typing import List, Optional, Any

import click
import requests

from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


def data_on_success_else_exit(api_response: requests.Response):
    """Returns the .data of a response if successful, else print error message and exit

    :param api_response:
    :return:
    """
    response_json = api_response.json()
    if response_json["success"]:
        return response_json["data"]

    log.debug(f"received: {response_json}")
    click.echo(JsonFormatter(response_json).format_with_double_quotes())
    sys.exit("The habitica API call wasn't successful")


class PrintableException(BaseException):
    """A BaseException that implements a default __str__"""

    def __init__(self, msg: str):
        super().__init__(PrintableException.__class__)
        self.msg = msg

    def __str__(self) -> str:
        return self.__class__.__name__ + ": " + self.msg


def case_insensitive_aliases(argument: str, choices: List[str], *,
                             raise_if_not_found=False):
    """Takes a potentially in-properly cased argument and returns
       the properly cased version"""
    # This function works but it very ugly:
    # @click.command(context_settings=dict(
    #       token_normalize_func= lambda x: case_insensitive_aliases(x, valid_food_names))
    # )

    for choice in choices:
        if argument.lower() == choice.lower():
            return choice

    if raise_if_not_found:
        raise ValueError(f"Could not match argument={argument} with choices={choices}")
    return argument


class EnhancedDate(click.DateTime):
    """EnhancedDate adds 'today' and 'tomorrow' keywords to the click.DateTime type."""
    name = "enhanceddate"

    def __init__(self):
        super().__init__(formats=["%Y-%m-%d", "%d-%m-%Y"])

        # This will add 'today' and 'tomorrow to the help message
        self.formats += ["today", "tomorrow"]

    def convert(self, value: Any, param: Optional["Parameter"], ctx: Optional["Context"]) -> Any:
        """Convert a value provided by the user into a datetime object."""
        if value == "today":
            return datetime.date.today()
        if value == "tomorrow":
            return datetime.date.today() + datetime.timedelta(days=1)

        return super().convert(value, param, ctx)
