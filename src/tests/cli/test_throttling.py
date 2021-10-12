#!/usr/bin/env python3
from datetime import datetime, date, time, timezone, timedelta
from typing import Any, Callable, List
from unittest.mock import MagicMock, patch

import pytest
from requests.structures import CaseInsensitiveDict

from hopla.hoplalib.http import ResponseHeaders
from hopla.hoplalib.throttling import ApiRequestThrottler, RateLimitingAwareThrottler


def is_close(a: float, b: float, epsilon=1e-3) -> bool:
    return abs(a - b) < epsilon


class TestApiRequestThrottler:

    def test__init__(self, ten_api_calls: List[Callable]):
        secs = 3
        call_limit = 12
        throttler = ApiRequestThrottler(ten_api_calls,
                                        throttle_seconds=secs,
                                        throttle_limit=call_limit)

        assert throttler.api_requests == ten_api_calls
        assert throttler.total_calls == len(ten_api_calls)
        assert throttler.throttle_limit == call_limit
        assert throttler.throttle_seconds == 3

    def test_release_without_throttle(self, two_api_requests: List[Callable]):
        throttler = ApiRequestThrottler(two_api_requests)

        call_releaser_result = throttler.release()
        first: Callable = call_releaser_result.__next__()
        second: Callable = call_releaser_result.__next__()
        with pytest.raises(StopIteration):
            call_releaser_result.__next__()

        assert first() == two_api_requests[0]()
        assert second() == two_api_requests[1]()

    def test_execute_all_request_with_throttle(self,
                                               three_api_requests: List[Callable],
                                               capsys):
        secs = 0.001
        throttler = ApiRequestThrottler(three_api_requests,
                                        throttle_limit=1,
                                        throttle_seconds=secs)

        throttler.execute_all_requests()

        captured = capsys.readouterr()
        expected_stderr_msg = \
            f"To prevent overheating Habitica, we'll wait {secs} seconds every request.\n"
        assert captured.err == expected_stderr_msg
        assert captured.out == "some api output"

    @pytest.mark.parametrize(
        "api_request,throttle_limit,expected_should_throttle", [
            ([], 10, False),
            ([lambda: 1, lambda: 2], 1, True),
            ([lambda: 1, lambda: 2], 2, False),
            ([lambda: 1, lambda: 2, lambda: 3], 3, False),
            ([lambda: "a"] * 12, 9, True),
            ([lambda: "a"] * 12, 17, False)
        ]
    )
    def test_exceeds_throttle_limit_noargs(self, api_request: List[Callable],
                                           throttle_limit: int,
                                           expected_should_throttle: bool):
        throttler = ApiRequestThrottler(api_request, throttle_limit=throttle_limit)

        result: bool = throttler.exceeds_throttle_limit()

        assert result == expected_should_throttle

    @pytest.fixture
    def two_api_requests(self) -> List[Callable[[None], Any]]:
        def f1() -> bool:
            return "Thermometer".islower()

        def f2() -> str:
            return "Nebuliser".upper()

        return [f1, f2]

    @pytest.fixture
    def three_api_requests(self, two_api_requests) -> List[Callable]:
        def f3():
            print("some api output", end="")

        return two_api_requests + [f3]

    @pytest.fixture
    def ten_api_calls(self) -> List[Callable[[None], None]]:
        def api_call():
            print("hi")

        return [api_call] * 10


class TestRateLimitingAwareThrottler:
    def test__init__empty_ok(self):
        empty_throttler = RateLimitingAwareThrottler()

        assert empty_throttler.api_requests == []
        assert empty_throttler._is_rate_initialized is False
        assert empty_throttler._xrate_limit_remaining is None
        assert empty_throttler._xrate_limit_reset is None
        assert empty_throttler._api_requests_remaining == 0

    def test_perform_and_yield_response_no_requests_ok(self):
        empty_throttler = RateLimitingAwareThrottler()

        response_generator = empty_throttler.perform_and_yield_response()

        with pytest.raises(StopIteration):
            next(response_generator)

    @patch("hopla.hoplalib.throttling.datetime")
    def test__calculate_sleep_time_wait_till_limit_ok(self, mock_datetime: MagicMock):
        # Testing internals here, feel free to improve.
        # This does circumvent actually 'sleeping' during the
        # tests, but time.sleep can be mocked too!
        throttler = RateLimitingAwareThrottler()
        throttler._xrate_limit_remaining = 0
        reset_datetime = datetime(year=2069, month=10, day=1,
                                  hour=0, minute=0, second=30,
                                  tzinfo=timezone.utc)
        throttler._xrate_limit_reset = reset_datetime

        secs_till_reset = 60
        mock_datetime.now.return_value = reset_datetime - timedelta(seconds=secs_till_reset)

        sleep_result_secs: float = throttler._calculate_sleep_time()

        expected_sleep: float = secs_till_reset + throttler.leeway_seconds + 5
        assert is_close(sleep_result_secs, expected_sleep)

    @pytest.mark.parametrize("secs_till_reset", [60, 40, 15, 10, 6.7])
    @patch("hopla.hoplalib.throttling.datetime")
    def test__calculate_sleep_time_requests_remaining_ok(self, mock_datetime: MagicMock,
                                                         secs_till_reset: float):
        # Testing internals here, feel free to improve.
        # This does circumvent actually 'sleeping' during the
        # tests, but time.sleep can be mocked too!
        throttler = RateLimitingAwareThrottler()
        xrate_limit_remaining = 15
        throttler._xrate_limit_remaining = xrate_limit_remaining
        reset_datetime = datetime(year=2069, month=10, day=1,
                                  hour=0, minute=0, second=30,
                                  tzinfo=timezone.utc)
        throttler._xrate_limit_reset = reset_datetime

        mock_datetime.now.return_value = reset_datetime - timedelta(seconds=secs_till_reset)

        sleep_result_secs: float = throttler._calculate_sleep_time()

        expected_sleep_without_leeway = secs_till_reset / xrate_limit_remaining
        expected_sleep: float = expected_sleep_without_leeway + throttler.leeway_seconds
        assert is_close(sleep_result_secs, expected_sleep)

    @patch("hopla.hoplalib.throttling.Response")
    def test_perform_and_yield_response_single_requests_ok(self,
                                                           mock_response: MagicMock):
        xrate_remaining = "29"
        xrate_reset = "Mon Oct 16 2022 13:49:39 GMT+0000 (Coordinated Universal Time)"
        headers = {
            ResponseHeaders.XRATE_LIMIT_REMAINING_HEADER_NAME: xrate_remaining,
            ResponseHeaders.XRATE_LIMIT_RESET_HEADER_NAME: xrate_reset
        }
        mock_response.headers = CaseInsensitiveDict(data=headers)
        throttler = RateLimitingAwareThrottler([(lambda: mock_response)])

        response_generator = throttler.perform_and_yield_response()

        assert throttler._is_rate_initialized is False
        assert throttler._api_requests_remaining == 1

        assert mock_response is next(response_generator)
        assert throttler._api_requests_remaining == 0

        assert throttler._is_rate_initialized is True
        assert throttler._xrate_limit_remaining == int(xrate_remaining)

        reset_datetime: datetime = throttler._xrate_limit_reset
        reset_date: date = reset_datetime.date()
        reset_time: time = reset_datetime.time()
        reset_timezone = reset_datetime.tzinfo
        assert reset_date == date(year=2022, month=10, day=16)
        assert reset_time == time(hour=13, minute=49, second=39)
        assert reset_timezone == timezone.utc

        with pytest.raises(StopIteration):
            next(response_generator)

    @patch("hopla.hoplalib.throttling.Response")
    @patch("hopla.hoplalib.throttling.Response")
    def test_perform_and_yield_response_multiple_requests_ok(self,
                                                             mock_response1: MagicMock,
                                                             mock_response2: MagicMock):
        xrate_remaining1 = "14"
        quick: datetime = datetime.now(timezone.utc) + timedelta(microseconds=100)
        xrate_reset1 = (
                quick.strftime('%a %b %d %Y %H:%M:%S %Z%z')
                + " (Coordinated Universal Time)"
        )
        headers1 = {
            ResponseHeaders.XRATE_LIMIT_REMAINING_HEADER_NAME: xrate_remaining1,
            ResponseHeaders.XRATE_LIMIT_RESET_HEADER_NAME: xrate_reset1
        }
        mock_response1.headers = headers1

        # hop from 14 to 10 is normal when executing concurrently
        xrate_remaining2 = "10"
        headers2 = {
            ResponseHeaders.XRATE_LIMIT_REMAINING_HEADER_NAME: xrate_remaining2,
            ResponseHeaders.XRATE_LIMIT_RESET_HEADER_NAME: xrate_reset1
        }
        mock_response2.headers = headers2

        throttler = RateLimitingAwareThrottler(api_requests=[
            lambda: mock_response1, lambda: mock_response2
        ])

        generator = throttler.perform_and_yield_response()

        assert throttler._api_requests_remaining == 2
        assert throttler._xrate_limit_remaining is None
        assert throttler._xrate_limit_reset is None

        response1 = next(generator)
        assert response1 == mock_response1
        assert throttler._api_requests_remaining == 1
        assert throttler._throttling_required() is False
        assert throttler._xrate_limit_remaining == int(xrate_remaining1)

        response2 = next(generator)
        assert response2 == mock_response2
        assert throttler._api_requests_remaining == 0
        assert throttler._throttling_required() is False
        assert throttler._xrate_limit_remaining == int(xrate_remaining2)

        with pytest.raises(StopIteration):
            next(generator)
