import logging

import click
import requests

from hopla.hoplalib.common import GlobalConstants
from hopla.hoplalib.http import UrlBuilder, RequestHeaders
from hopla.hoplalib.clickutils import data_on_success_else_exit

log = logging.getLogger()


@click.command()
@click.option("--gems", type=int, default=4)
def support_development(gems):
    """Support the development of hopla

    [APIdocs](https://habitica.com/apidoc/#api-Member-TransferGems)

    \f
    :param gems:
    :return:
    """
    log.debug(f"hopla support-development gems={gems}")
    url = UrlBuilder(path_extension="/members/transfer-gems").url
    headers = RequestHeaders().get_default_request_headers()

    params = {
        "message": "Thanks!",
        "toUserId": GlobalConstants.DEVELOPMENT_UUID,
        "gemAmount": gems
    }

    support_development_request = requests.Request(
        method="POST", url=url, headers=headers, json=params
    )
    response = requests.session().send(support_development_request.prepare())
    response_data = data_on_success_else_exit(response)
    click.echo(response_data)
