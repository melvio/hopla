import requests
import click
import logging

from hopla.hoplalib.OutputFormatter import JsonFormatter

log = logging.getLogger()


def data_on_success_else_exit(api_response: requests.Response):
    """Returns the .data of a response if successful, else print error message and exit

    :param api_response:
    :return:
    """
    response_json = api_response.json()
    if response_json["success"]:
        return response_json["data"]
    else:
        log.debug(f"received: {response_json}")
        click.echo(JsonFormatter(response_json).format_with_double_quotes())
        exit()  # TODO: not sure if needed