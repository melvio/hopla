#!/usr/bin/env python3

import pytest
from click.testing import CliRunner, Result
from unittest.mock import patch, MagicMock
from requests.status_codes import codes

from hopla.cli.feed_all import feed_all
from hopla.cli.groupcmds.get_user import HabiticaUser
from hopla.hoplalib.hopla_option import NO_INTERACTION_OPTION_NAMES


class MockBadGatewayResponse:
    def __init__(self, msg):
        self.status_code = codes.bad_gateway
        self.__json = {"success": False, "error": "BadGateway", "message": msg}

    def json(self):
        return self.__json


class MockOkResponse:
    def __init__(self, msg: str):
        self.status_code = codes.ok
        self.__json = {"success": True, "message": msg}

    def json(self):
        return self.__json


class TestFeedAllCliCommand:
    yes_responses = ["y", "Y", "yes", "Yes", "YES"]
    no_responses = ["n", "N", "no", "No", "NO", "", "anything else"]
    released_zoo_users = [
        HabiticaUser({
            "items": {"pets": {"Seahorse-White": 0},
                      "mounts": {"Seahorse-White": None},
                      "food": {"Milk": 20}}
        }),
        HabiticaUser({
            "items": {"pets": {"Egg-White": 0},
                      "mounts": {"Egg-White": True},
                      "food": {"Milk": 10}}
        })
    ]

    @pytest.mark.parametrize("no_response", no_responses)
    @patch("hopla.cli.feed_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_feed_all_pets_user_aborts(self,
                                       mock_user_request: MagicMock,
                                       no_response: str,
                                       user_with_feedable_pet: HabiticaUser):
        mock_user_request.return_value = user_with_feedable_pet
        runner = CliRunner()
        result: Result = runner.invoke(feed_all, input=no_response)

        assert "Aborted!" in result.stdout
        assert result.exit_code == 1

    @patch("hopla.cli.feed_all.HabiticaUserRequest.request_user")
    def test_feed_all_api_bad_gateway_fail(self, mock_user_request: MagicMock):
        bad_gateway_msg = "Service responded with a status of 502 (Bad Gateway)"
        mock_user_request.return_value = MockBadGatewayResponse(msg=bad_gateway_msg)

        runner = CliRunner()
        result: Result = runner.invoke(feed_all, input="Yes")

        assert result.exit_code == 1
        assert bad_gateway_msg in result.stdout

    @patch("hopla.cli.feed_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_feed_all_empty_plan_ok(self,
                                    mock_user_request: MagicMock,
                                    user_with_no_feedable_pets: HabiticaUser):
        mock_user_request.return_value = user_with_no_feedable_pets

        runner = CliRunner()
        result: Result = runner.invoke(feed_all, input="Yes")

        assert result.exit_code == 0
        assert result.stdout.startswith("The feed plan is empty.")

    @pytest.mark.parametrize("yes_response", yes_responses)
    @patch("hopla.cli.feed_all.RateLimitingAwareThrottler.perform_and_yield_response")
    @patch("hopla.cli.feed_all.FeedPostRequester.post_feed_request")
    @patch("hopla.cli.feed_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_feed_all_ok(self,
                         mock_user_request: MagicMock,
                         mock_feed_request: MagicMock,
                         mock_throttle_iter: MagicMock,
                         user_with_feedable_pet: HabiticaUser,
                         yes_response: str):
        # This user has a pet that can be grown into a mount by feeding 8 Fish
        mock_user_request.return_value = user_with_feedable_pet

        feed_msg = "You have tamed Skeleton Velociraptor, let's go for a ride!"
        mocked_response = MockOkResponse(msg=feed_msg)
        mock_feed_request.return_value = mocked_response
        mock_throttle_iter.return_value = iter([mocked_response])

        runner = CliRunner()
        result: Result = runner.invoke(feed_all, input=yes_response)

        expected_plan = "Pet Velociraptor-Skeleton will get 8 Fish."
        expected_prompt = f"Do you want to proceed? [y/N]: {yes_response}"

        assert result.stdout == f"{expected_plan}\n{expected_prompt}\n{feed_msg}\n"
        assert result.exit_code == 0

    @pytest.mark.parametrize("force_option", NO_INTERACTION_OPTION_NAMES)
    @patch("hopla.cli.feed_all.RateLimitingAwareThrottler.perform_and_yield_response")
    @patch("hopla.cli.feed_all.FeedPostRequester.post_feed_request")
    @patch("hopla.cli.feed_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_feed_all_force_ok(self,
                               mock_user_request: MagicMock,
                               mock_feed_request: MagicMock,
                               mock_throttle_iter: MagicMock,
                               user_with_feedable_pet: HabiticaUser,
                               force_option: str):
        # This user has a pet that can be grown into a mount by feeding 8 Fish
        mock_user_request.return_value = user_with_feedable_pet

        feed_msg = "You have tamed Skeleton Velociraptor, let's go for a ride!"
        mocked_response = MockOkResponse(msg=feed_msg)
        mock_feed_request.return_value = mocked_response
        mock_throttle_iter.return_value = iter([mocked_response])

        runner = CliRunner()
        result: Result = runner.invoke(feed_all, [force_option])

        assert result.stdout == f"{feed_msg}\n"
        assert result.exit_code == 0

    @pytest.mark.parametrize("yes_response", yes_responses)
    @pytest.mark.parametrize("released_zoo_user", released_zoo_users)
    @patch("hopla.cli.feed.HabiticaUserRequest.request_user_data_or_exit")
    def test_feed_released_pets(self, mock_user_request: MagicMock,
                                released_zoo_user: HabiticaUser,
                                yes_response: str):
        mock_user_request.return_value = released_zoo_user

        runner = CliRunner()
        result: Result = runner.invoke(feed_all, input=yes_response)

        expected_msg = ("The feed plan is empty. Reasons for this could be:\n"
                        "1. There is insufficient food available to turn pets into mounts.\n"
                        "2. You don't have any feedable pets.")
        assert expected_msg in result.stdout

    @pytest.fixture
    def user_with_feedable_pet(self) -> HabiticaUser:
        return HabiticaUser({"items": {
            "pets": {"Velociraptor-Skeleton": 10},
            "mounts": {},
            "food": {"Fish": 20}
        }})

    @pytest.fixture
    def user_with_no_feedable_pets(self) -> HabiticaUser:
        return HabiticaUser({"items": {
            "pets": {},
            "mounts": {},
            "food": {"Fish": 20}
        }})
