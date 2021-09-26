#!/usr/bin/env python3
"""
Module with throttling logic.
"""
from dataclasses import dataclass
from typing import Callable, Any
from time import sleep

import click


@dataclass
class ApiRequestThrottler:
    """
    An object that manages a list of api requests.
    """

    def __init__(self, api_requests: [Callable[[None], Any]],
                 *, throttle_seconds: float = 2.5,
                 throttle_threshold: int = 25):
        self.api_requests = api_requests
        self.total_calls = len(api_requests)
        self.throttle_seconds = throttle_seconds
        """How long to wait between api calls that are throttled."""
        self.throttle_threshold = throttle_threshold
        """Maximum of calls that you can do without throttling."""

    def release(self):
        """Yields the next api requests ready to be executed.

        :return:
        """
        throttle_enabled: bool = self.exceeds_throttle_limit(api_call_times=self.total_calls)

        if throttle_enabled:
            click.echo(f"To prevent overheating Habitica, we'll "
                       f"buy once every {self.throttle_seconds} seconds",
                       err=True)

        for api_request in self.api_requests:
            yield api_request
            if throttle_enabled:
                self.throttle()

    def throttle(self):
        """Wait before executing the next api request."""
        sleep(self.throttle_seconds)

    def exceeds_throttle_limit(self, *, api_call_times: int) -> bool:
        """Return True if we need Hopla to go easy on the Habitica API."""
        return api_call_times > self.throttle_threshold
