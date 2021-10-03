#!/usr/bin/env python3
"""
A module with helper functions for the `hopla feed` and `hopla feed-all`
CLI commands.
"""
import sys
from typing import NoReturn, Union

import click
import requests

from hopla.hoplalib.outputformatter import JsonFormatter


def get_feed_data_or_exit(feed_response: requests.Response) -> Union[NoReturn, dict]:
    """
    Given a feed response, if the API request was successful, return interesting
    feed information. On failure, exit with an error message.
    """
    response_json = feed_response.json()
    if response_json["success"]:
        feed_data = {
            "feed_status": response_json["data"],
            "message": response_json["message"]
        }

        click.echo(JsonFormatter(feed_data).format_with_double_quotes())
        return feed_data

    click.echo(response_json["message"])
    sys.exit(1)
