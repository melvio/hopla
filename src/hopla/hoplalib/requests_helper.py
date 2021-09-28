#!/usr/bin/env python3
"""
A module with helper functions for the requests package.
"""
import logging
import sys
from typing import Any, NoReturn, Union

import requests
import click

from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


def get_data_or_exit(api_response: requests.Response) -> Union[NoReturn, Any]:
    """Returns the "data" of a response if successful, else print error message and exit

    :param api_response:
    :return:
    """
    response_json = api_response.json()
    if response_json["success"]:
        return response_json["data"]

    __failed_to_get_data_so_exit(response_json=response_json,
                                 status_code=api_response.status_code)


def __failed_to_get_data_so_exit(response_json,
                                 status_code: int) -> NoReturn:
    log.debug(f"received: {response_json=}")
    click.echo(JsonFormatter(response_json).format_with_double_quotes())
    sys.exit(f"The habitica API call failed: {status_code=}")
