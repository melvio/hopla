#!/usr/bin/env python3
from typing import Any, Callable, List

import pytest

from hopla.hoplalib.throttling import ApiRequestThrottler


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
