#!/usr/bin/env python3
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner, Result

from hopla.cli.hatch_all import hatch_all, to_pet_list
from hopla.hoplalib.hopla_option import NO_INTERACTION_OPTION_NAMES
from hopla.hoplalib.user.usermodels import HabiticaUser
from hopla.hoplalib.zoo.foodmodels import FeedStatus
from hopla.hoplalib.zoo.petmodels import Pet


class MockThrottler:
    def __init__(self, *, response1: str, response2: str):
        self.response1 = response1
        self.response2 = response2

    def release(self):
        yield lambda: self.response1
        yield lambda: self.response2


class MockOkHatchResponse:
    def __init__(self, msg):
        self.msg = msg

    def json(self):
        return {"success": True, "message": self.msg}


class TestHatchAllCliCommand:

    @patch("hopla.cli.hatch_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_hatch_all_nothing_to_hatch_fail(self, mock_user_request: MagicMock):
        nothing_to_hatch_user = HabiticaUser({"items": {
            "pets": {"Wolf-Base": 5},
            "eggs": {"Wolf": 2},
            "hatchingPotions": {"Base": 1}
        }})
        mock_user_request.return_value = nothing_to_hatch_user

        runner = CliRunner()
        result: Result = runner.invoke(hatch_all)

        assert result.exit_code == 1
        assert result.stdout == (
            "The hatch plan is empty. Do you have enough eggs and hatching potions?\n"
            "Exiting\n"
        )

    @patch("hopla.cli.hatch_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_hatch_all_something_to_hatch_user_denies_ok(self, mock_user_request: MagicMock):
        egg_name = "Wolf"
        potion1_name = "Base"
        potion2_name = "Fluorite"
        mock_user_request.return_value = HabiticaUser({"items": {
            "pets": {"Turtle-White": 15},
            "eggs": {egg_name: 2},
            "hatchingPotions": {potion1_name: 1, potion2_name: 1}
        }})

        runner = CliRunner()
        user_denies_input: str = "No"
        result: Result = runner.invoke(hatch_all, input=user_denies_input)

        expected_msg = (
            f"A {egg_name} egg will be hatched by a {potion1_name} potion.\n"
            f"A {egg_name} egg will be hatched by a {potion2_name} potion.\n"
            f"Do you wish to proceed? [y/N]: {user_denies_input}\n"
            "No eggs were hatched.\n"
        )
        # User denying is not an error. This is part of the normal flow. So we want a 0.
        assert result.exit_code == 0
        assert result.stdout.endswith(expected_msg)

    @patch("hopla.cli.hatch_all.RateLimitingAwareThrottler.perform_and_yield_response")
    @patch("hopla.cli.hatch_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_hatch_all_something_to_hatch_user_confirms_ok(self,
                                                           mock_user_request: MagicMock,
                                                           mock_throttler: MagicMock):
        egg_name = "Wolf"
        potion1_name = "Base"
        potion2_name = "Fluorite"
        mock_user_request.return_value = HabiticaUser({"items": {
            "pets": {},
            "eggs": {egg_name: 2},
            "hatchingPotions": {potion1_name: 1, potion2_name: 1}
        }})

        msg1 = f"Successfully hatched a {egg_name}-{potion1_name}."
        msg2 = f"Successfully hatched a {egg_name}-{potion2_name}."
        response1 = MockOkHatchResponse(msg1)
        response2 = MockOkHatchResponse(msg2)

        mock_throttler.return_value = iter([response1, response2])

        runner = CliRunner()
        user_confirms_input: str = "yes"
        result: Result = runner.invoke(hatch_all, input=user_confirms_input)

        expected_msg = (
            f"A {egg_name} egg will be hatched by a {potion1_name} potion.\n"
            f"A {egg_name} egg will be hatched by a {potion2_name} potion.\n"
            f"Do you wish to proceed? [y/N]: {user_confirms_input}\n"
            f"{msg1}\n"
            f"{msg2}\n"
        )
        assert result.exit_code == 0
        assert result.stdout == expected_msg

    @pytest.mark.parametrize("force_option", NO_INTERACTION_OPTION_NAMES)
    @patch("hopla.cli.hatch_all.RateLimitingAwareThrottler.perform_and_yield_response")
    @patch("hopla.cli.hatch_all.HabiticaUserRequest.request_user_data_or_exit")
    def test_hatch_all_something_to_hatch_force_ok(self,
                                                   mock_user_request: MagicMock,
                                                   mock_throttler: MagicMock,
                                                   force_option: str):
        egg_name = "Wolf"
        potion1_name = "Base"
        potion2_name = "Fluorite"
        mock_user_request.return_value = HabiticaUser({"items": {
            "pets": {},
            "eggs": {egg_name: 2},
            "hatchingPotions": {potion1_name: 1, potion2_name: 1}
        }})

        msg1 = f"Successfully hatched a {egg_name}-{potion1_name}."
        msg2 = f"Successfully hatched a {egg_name}-{potion2_name}."
        response1 = MockOkHatchResponse(msg1)
        response2 = MockOkHatchResponse(msg2)

        mock_throttler.return_value = iter([response1, response2])

        runner = CliRunner()
        result: Result = runner.invoke(hatch_all, [force_option])

        assert result.exit_code == 0
        assert result.stdout == f"{msg1}\n{msg2}\n"


class TestToPetList:
    def test_to_pet_list_empty_dict_ok(self):
        result: List[Pet] = to_pet_list({})
        assert result == []

    def test_to_pet_list_ok(self):
        pet1, feed_status1 = "Wolf-Base", 5
        pet2, feed_status2 = "Axolotl-Red", 10
        pet3, feed_status3 = "Rat-White", -1
        pet4, feed_status4 = "Turtle-Golden", 0

        pets: Dict[str, int] = {
            pet1: feed_status1, pet2: feed_status2,
            pet3: feed_status3, pet4: feed_status4
        }

        result: List[Pet] = to_pet_list(pets)

        expected: List[Pet] = [
            Pet(pet1, feed_status=FeedStatus(feed_status1)),
            Pet(pet2, feed_status=FeedStatus(feed_status2)),
            Pet(pet3, feed_status=FeedStatus(feed_status3)),
            Pet(pet4, feed_status=FeedStatus(feed_status4))
        ]
        assert result == expected
