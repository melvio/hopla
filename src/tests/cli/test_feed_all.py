#!/usr/bin/env python3
import pytest
from click.testing import CliRunner, Result
from unittest.mock import patch, MagicMock
from requests.status_codes import codes

from hopla.cli.feed_all import feed_all
from hopla.cli.groupcmds.get_user import HabiticaUser


class MockBadGatewayResponse:
    def __init__(self, msg):
        self.status_code = codes.bad_gateway
        self.__json = {"success": False, "error": "BadGateway", "message": msg}

    def json(self):
        return self.__json


class MockOkResponse:
    def __init__(self, msg: str):
        self.status_code = codes.ok
        self.__json = {"success": True, "data": -1, "message": msg}

    def json(self):
        return self.__json


class TestFeedAllCliCommand:

    @pytest.mark.parametrize(
        "no_response", [
            "n", "N", "no", "No", "NO", "", "anything else"
        ]
    )
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

    @pytest.mark.parametrize("yes_response", ["y", "Y", "yes", "Yes", "YES"])
    @patch("hopla.cli.feed_all.FeedPostRequester.post_feed_request")
    @patch("hopla.cli.feed_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_feed_all_ok(self,
                         mock_user_request: MagicMock,
                         mock_feed_request: MagicMock,
                         user_with_feedable_pet: HabiticaUser,
                         yes_response: str):
        # This user has a pet that can be grown into a mount by feeding 8 Fish
        mock_user_request.return_value = user_with_feedable_pet

        feed_msg = "You have tamed Skeleton Velociraptor, let's go for a ride!"
        mock_feed_request.return_value = MockOkResponse(msg=feed_msg)

        runner = CliRunner()
        result: Result = runner.invoke(feed_all, input=yes_response)

        assert "Pet Velociraptor-Skeleton will get 8 Fish.\n" in result.stdout
        assert f"Do you want to proceed? [y/N]: {yes_response}\n" in result.stdout
        assert feed_msg in result.stdout
        assert '"feeding_status": -1' in result.stdout
        assert result.exit_code == 0

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
