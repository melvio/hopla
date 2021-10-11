#!/usr/bin/env python3
"""
Module with throttling logic.
"""
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Any, Callable, List, Optional

import click
from requests import Response
from requests.structures import CaseInsensitiveDict

from hopla.hoplalib.http import ResponseHeaders


@dataclass
class ApiRequestThrottler:
    """
    An object that manages a list of api requests.
    """

    def __init__(self, api_requests: List[Callable[[], Any]],
                 *, throttle_seconds: float = 2.5,
                 throttle_limit: int = 25):
        self.api_requests = api_requests
        self.total_calls = len(api_requests)
        self.throttle_seconds = throttle_seconds
        """How long to wait between api calls that are throttled."""
        self.throttle_limit = throttle_limit
        """Maximum of calls that you can do without throttling."""

    def release(self):
        """Yields the next api requests ready to be executed.

        :return:
        """
        throttle_enabled: bool = self.exceeds_throttle_limit()

        if throttle_enabled:
            click.echo(f"To prevent overheating Habitica, we'll "
                       f"wait {self.throttle_seconds} seconds every request.",
                       err=True)

        for api_request in self.api_requests:
            yield api_request
            if throttle_enabled:
                self.throttle()

    def execute_all_requests(self) -> None:
        """Execute all API request and discard the return values."""
        for api_request in self.release():
            _ = api_request()

    def throttle(self):
        """Wait before executing the next api request."""
        sleep(self.throttle_seconds)

    def exceeds_throttle_limit(self, *,
                               api_call_times: Optional[int] = None) -> bool:
        """Return True if we need Hopla to go easy on the Habitica API."""
        call_times: int = api_call_times or self.total_calls
        return call_times > self.throttle_limit


@dataclass
class RateLimitingAwareThrottler:
    """
    Throttler that slows down a list of requests based on HTTP rate-limiting
    headers. This throttler acts as a queue of API requests and its
    `perform_and_yield_response` function acts as a dispatcher.

    [WIKI](https://habitica.fandom.com/wiki/Guidance_for_Comrades#Rate_Limiting)
    """
    api_requests: List[Callable[[], Response]] = field(default_factory=list)
    leeway_seconds: float = 0.1
    """Number of seconds to wait over the requested limit."""
    _is_first: bool = field(init=False, default=True)
    """
    Value derived from the X-RateLimit-Remaining header.

    The number of remaining requests that can be made in the current 60 second
    period.
    """

    def __post_init__(self):
        self._api_requests_remaining = len(self.api_requests)
        self._xrate_limit_remaining: Optional[int] = None
        self._xrate_limit_reset: Optional[datetime] = None

    def perform_and_yield_response(self):
        """
        Execute the next request. This function acts as a dispatcher.
        :return:
        """
        for api_request in self.api_requests:
            if self._is_first is True:
                # Always skip throttling for the first request because
                # we don't have any rate limiting information.
                self._is_first = False
            elif self._throttling_required():
                self._throttle()

            response: Response = api_request()
            self._set_xrate_limit_remaining(response.headers)
            self._set_xrate_limit_reset(response.headers)
            # Consider dequeueing from a queue instead calculating remaining requests.
            self._api_requests_remaining -= 1

            yield response

    def _throttling_required(self) -> bool:
        """Return True when queue is relatively long compared to xrate-limit."""
        return self._api_requests_remaining >= self._xrate_limit_remaining

    def _throttle(self) -> None:
        """Sleep the required time."""
        time.sleep(self._calculate_sleep_time())

    def _calculate_sleep_time(self) -> float:
        """
        Calculate how many seconds to sleep to evenly spread out the
        API requests over the remaining xrate reset time.
        """
        now_utc: datetime = datetime.now(timezone.utc)
        time_till_reset: timedelta = self._xrate_limit_reset - now_utc

        if self._xrate_limit_remaining == 0:
            sleep_time: float = time_till_reset.total_seconds()
        else:
            time_interval: timedelta = time_till_reset / self._xrate_limit_remaining
            sleep_time: float = time_interval.total_seconds()

        # use max(..., 0) for when x-rate limit is in the past.
        return max(sleep_time + self.leeway_seconds, 0)

    def _set_xrate_limit_remaining(self, headers: CaseInsensitiveDict):
        """Set the xrate_limit_remaining from a given Habitica API response headers."""
        calls_remaining: str = headers[ResponseHeaders.XRATE_LIMIT_REMAINING_HEADER_NAME]
        self._xrate_limit_remaining = int(calls_remaining)

    def _set_xrate_limit_reset(self, headers: CaseInsensitiveDict):
        """Set the xrate_limit_reset from a given Habitica API response headers."""
        reset_datetime_str: str = headers[ResponseHeaders.XRATE_LIMIT_RESET_HEADER_NAME]
        self._xrate_limit_reset = datetime.strptime(
            reset_datetime_str.split(" (")[0],  # oef... painful
            "%a %b %d %Y %H:%M:%S %Z%z"
            # example:
            # "Mon Oct 16 2022 13:49:39 GMT+0000 (Coordinated Universal Time)",
        )
