#!/usr/bin/env python3
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner, Result

from hopla.cli.hatch import hatch


class MockHatchResponse:
    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


class MockHatchRequester:
    def __init__(self, response_json):
        self._response_json = response_json

    def post_hatch_egg_request(self):
        return MockHatchResponse(self._response_json)


class TestHatchCliCommand:
    # https://habitica.com/apidoc/#api-User-UserHatch

    @pytest.mark.parametrize("pet_name,potion_name", [
        ("Gryphon", "Base"),
        ("Hedgehog", "Red"),
    ])
    @patch("hopla.cli.hatch.HatchRequester")
    def test_hatch_egg_ok(self, feed_requester_mock: MagicMock,
                          pet_name: str, potion_name: str):
        json: dict = {
            "success": True,
            "data": {"user.items": "way to much stuff here"},
            "message": "Your egg hatched! Visit your stable to equip your pet."
        }
        feed_requester_mock.return_value = MockHatchRequester(response_json=json)

        runner = CliRunner()
        result: Result = runner.invoke(hatch, [pet_name, potion_name])

        assert result.stdout == f"Successfully hatched a {pet_name}-{potion_name}.\n"
        assert result.exit_code == 0

    @pytest.mark.parametrize("error,message", [
        ("NotAuthorized", "You already have that pet. Try hatching a different combination!"),
        ("NotFound", "You're missing either that egg or that potion"),
    ])
    @patch("hopla.cli.hatch.HatchRequester")
    def test_hatch_egg_fail(self, feed_requester_mock: MagicMock,
                            error: str, message: str):
        json: dict = {"success": False, "error": error, "message": message}
        feed_requester_mock.return_value = MockHatchRequester(response_json=json)

        runner = CliRunner()
        result: Result = runner.invoke(hatch, ["Frog", "White"])

        assert result.stdout == f"{error}: {message}\n"
        assert result.exit_code == 1

    @pytest.mark.parametrize("pet_name,potion_name", [
        ("LionCub", "MossyStone"),
        ("Wolf", "Shade"),
        ("Dragon", "Ember"),
        ("Cactus", "SolarSystem"),
        ("PandaCub", "Veggie")
    ])
    @patch("hopla.cli.hatch.HatchRequester")
    def test_hatch_ok(self, feed_requester_mock: MagicMock, pet_name: str, potion_name: str):
        json: dict = {
            "success": True,
            "data": {"user.items": "way to much stuff here"},
            "message": "Your egg hatched! Visit your stable to equip your pet."
        }
        feed_requester_mock.return_value = MockHatchRequester(response_json=json)

        runner = CliRunner()
        result: Result = runner.invoke(hatch, [pet_name, potion_name])

        assert result.stdout == f"Successfully hatched a {pet_name}-{potion_name}.\n"
        assert result.exit_code == 0

    @pytest.mark.parametrize("error,message", [
        ("NotAuthorized", "You already have that pet. Try hatching a different combination!"),
        ("NotFound", "You're missing either that egg or that potion"),
    ])
    @patch("hopla.cli.hatch.HatchRequester")
    def test_hatch_fail(self, feed_requester_mock: MagicMock, error: str, message: str):
        json: dict = {"success": False, "error": error, "message": message}
        feed_requester_mock.return_value = MockHatchRequester(response_json=json)

        runner = CliRunner()
        result: Result = runner.invoke(hatch, ["LionCub", "Zombie"])

        assert result.stdout == f"{error}: {message}\n"
        assert result.exit_code == 1
