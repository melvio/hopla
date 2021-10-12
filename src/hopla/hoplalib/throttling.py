#!/usr/bin/env python3
"""
Module with throttling logic.
"""
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Any, Callable, Iterator, List, Optional

import click
from requests import Response
from requests.structures import CaseInsensitiveDict

from hopla.hoplalib.http import ResponseHeaders

log = logging.getLogger()


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

    def release(self) -> Iterator[Any]:
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

    def throttle(self) -> None:
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
    api_requests: List[Callable[[], Response]] = field(
        default_factory=list,
        repr=False
    )
    """The queue of API requests. (Currently implemented as a list.)"""
    leeway_seconds: float = 0.25
    """Number of seconds to wait over the requested limit."""
    _is_rate_initialized: bool = field(init=False, default=False)
    """We only know rate limiting information after the first API request."""
    _xrate_limit_remaining: Optional[int] = field(init=False, default=None)
    """
    The number of remaining requests that can be made in the current
    60 second period.

    This value is derived from the X-RateLimit-Remaining header and
    is initialized to None because we won't know it yet at the first
    initialization.
    """

    _xrate_limit_reset: Optional[datetime] = field(init=False, default=None)
    """
    The time on which the current rate-limit will be reset.

    This value derived from the X-RateLimit-Reset header and
    is initialized to None because we won't know it yet at the first
    initialization.
    """

    def __post_init__(self):
        # pylint: disable=pointless-string-statement
        # I think pylint doesn't recognize that these strings act as documentation
        # in the __post_init__ function.

        self._api_requests_remaining: int = len(self.api_requests)
        """The number of Api requests that we haven't executed yet."""

    def perform_and_yield_response(self) -> Iterator[Response]:
        """
        Execute the next request. This function acts as a dispatcher.
        :return:
        """
        for api_request in self.api_requests:
            log.debug(self)
            if self._is_rate_initialized is True and self._throttling_required():
                self._throttle()

            response: Response = api_request()
            self.__update_rate_info(response)

            yield response

    def __update_rate_info(self, response: Response):
        """Use the response to update rate limiting information"""
        self._set_xrate_limit_remaining(response.headers)
        self._set_xrate_limit_reset(response.headers)
        # Consider dequeueing from a queue instead calculating remaining requests.
        self._api_requests_remaining -= 1
        self._is_rate_initialized = True

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
            # No request remains. Let's chill out a lot.
            sleep_time: float = time_till_reset.total_seconds() + 5.
        elif self._xrate_limit_remaining == 1:
            # Only 1 request remains. Let's chill out.
            sleep_time: float = time_till_reset.total_seconds() + 3
        elif self._xrate_limit_remaining == 2:
            # Only 2 requests remain. By slowing down in this manner, we can run
            # hopla commands concurrently.
            sleep_time: float = time_till_reset.total_seconds() + 2
        else:
            # Go fast.
            time_interval: timedelta = time_till_reset / self._xrate_limit_remaining
            sleep_time: float = time_interval.total_seconds()

        # use max(..., 0) for when x-rate limit is in the past.
        return max(sleep_time, 0) + self.leeway_seconds

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
