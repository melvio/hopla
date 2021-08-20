#!/usr/bin/env python3
import sys
import os

sys.path.append(os.environ.get("script_dirname"))

import requests
from argparse import ArgumentParser, Namespace

# TODO: temporary, while hopla is in beta
try:
    # cmdline
    from hoplalib.Http import UrlBuilder, RequestHeaders
except:
    # jetbrains
    from hopla.hoplalib.Http import UrlBuilder, RequestHeaders


class DayStartArgumentParser:
    DAY_START_USER_ARGUMENT = "day_start"

    def __init__(self, arg_parser: ArgumentParser = None):
        if arg_parser is None:
            self.arg_parser = ArgumentParser()
        else:
            self.arg_parser = arg_parser

        self.arg_parser.add_argument(
            DayStartArgumentParser.DAY_START_USER_ARGUMENT,
            nargs="?",
            help="the hour to start your habitica day",
            type=int,
            default=0,
            choices=range(0, 24)
        )

    @property
    def day_start(self) -> int:
        # parsing every time is cheap; it is just 1 value the user supplies
        args: Namespace = self.arg_parser.parse_args()
        return args.day_start


class DayStartJsonCreator:
    DAY_START_KEY = "dayStart"

    def __init__(self, *, day_start: int):
        self.day_start = day_start

    def _create_post_content(self) -> dict:
        return {DayStartJsonCreator.DAY_START_KEY: self.day_start}

    @property
    def json_content(self) -> dict:
        post_content: dict = self._create_post_content()
        # todo: instead of asserts use unittests
        assert len(post_content) != 0, "created json is empty"

        return post_content


class DayStartPostRequester:
    def __init__(self, *,
                 json_body: dict,
                 request_headers: dict):
        self.json_body = json_body
        self.request_headers = request_headers

    @property
    def path(self) -> str:
        return "/user/custom-day-start"

    @property
    def custom_day_start_url(self) -> str:
        return UrlBuilder(path_extension=self.path).url

    def post_day_start(self) -> requests.Response:
        return requests.post(
            url=self.custom_day_start_url,
            headers=self.request_headers,
            json=self.json_body
        )


if __name__ == "__main__":
    headers = RequestHeaders().get_default_request_headers()
    json_content = DayStartJsonCreator(day_start=DayStartArgumentParser().day_start).json_content
    day_start_request = DayStartPostRequester(request_headers=headers,
                                              json_body=json_content)
    response = day_start_request.post_day_start()

    # TODO: (contact:melvio) provide debug logging in python scripts
    # TODO: (contact:melvio) provide nice use interaction for python scripts
    print(response.json())