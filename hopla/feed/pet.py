#!/usr/bin/env python3

import sys
import os

sys.path.append(os.environ.get("script_dirname"))

# TODO: temporary, while hopla is in beta
try:
    # cmdline
    from hoplalib.Authorization import AuthorizationHandler
    from hoplalib.Http import UrlBuilder, RequestHeaders
except Exception:
    # jetbrains
    from hopla.hoplalib.Authorization import AuthorizationHandler
    from hopla.hoplalib.Http import UrlBuilder, RequestHeaders

import requests
from argparse import ArgumentParser, Namespace


class FeedPetParser:
    PET_USER_ARGUMENT = "pet_name"
    FOOD_USER_ARGUMENT = "food_name"

    def __init__(self, arg_parser: ArgumentParser = None):
        if arg_parser is None:
            self.arg_parser = ArgumentParser()
        else:
            self.arg_parser = arg_parser

        self.arg_parser.add_argument(
            FeedPetParser.PET_USER_ARGUMENT,
            help="the pet name",
            type=str,
        )

        self.arg_parser.add_argument(
            FeedPetParser.FOOD_USER_ARGUMENT,
            help="the pet name",
            type=str
        )

    @property
    def pet_name(self) -> str:
        args: Namespace = self.arg_parser.parse_args()
        return args.pet_name

    @property
    def food_name(self) -> str:
        args: Namespace = self.arg_parser.parse_args()
        return args.food_name


class PetFeedPostRequester:
    """
    The PetFeedPostRequester sends a post request to feed a pet.

    Note: this API endpoint expects query params instead
    of a request body (even though it is a HTTP POST).

    [APIDOCS](https://habitica.com/apidoc/#api-User-UserFeed)
    """

    def __init__(self, *,
                 request_headers: dict,
                 pet_name: str,
                 food_name: str,
                 food_amount: int = 1):
        self.request_headers = request_headers
        self.pet_name = pet_name
        self.food_name = food_name
        self.query_params = {"amount": food_amount}

    @property
    def path(self) -> str:
        return f"/user/feed/{self.pet_name}/{self.food_name}"

    @property
    def feed_pet_food_url(self) -> str:
        return UrlBuilder(path_extension=self.path).url

    def post_feed_pet_food(self) -> requests.Response:
        return requests.post(
            url=self.feed_pet_food_url,
            headers=self.request_headers,
            params=self.query_params
        )


if __name__ == "__main__":
    headers = RequestHeaders().get_default_request_headers()
    feed_pet_food_parser = FeedPetParser()
    feed_pet_food_request = PetFeedPostRequester(
        request_headers=headers,
        pet_name=feed_pet_food_parser.pet_name,
        food_name=feed_pet_food_parser.food_name
        # TODO: get an amount from the user
    )

    response: requests.Response = feed_pet_food_request.post_feed_pet_food()

    # TODO: (contact:melvio) handle terminal output
    print(response.text)
