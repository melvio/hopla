#!/usr/bin/env python3
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner, Result

from hopla.cli.cast import cast, times_until_out_of_mana
from hopla.hoplalib.cast.spellmodel import Spell


class MockCastResponse:
    def __init__(self, success: bool,
                 user_mp: float,
                 message: Optional[str],
                 error: Optional[str],
                 status_code: int):
        self.success = success
        self.user_mp = user_mp
        self.message = message
        self.error = error
        self.status_code = status_code

    def json(self) -> dict:
        if self.success is True:
            return {
                "success": self.success,
                "data": {"user": {"stats": {"mp": self.user_mp}}}
            }

        return {
            "success": self.success,
            "message": self.message,
            "error": self.error
        }


class MockCastRequest:

    def __init__(self, success: bool, remaining_user_mana: float = 0.0,
                 message: Optional[str] = None, error: Optional[str] = None,
                 status_code: int = 200):
        self.success = success
        self.user_mp = remaining_user_mana
        self.message = message
        self.error = error
        self.status_code = status_code

    def post_spell(self):
        return MockCastResponse(success=self.success, user_mp=self.user_mp,
                                message=self.message, error=self.error,
                                status_code=self.status_code)


class TestCastCliCommand:
    @patch("hopla.cli.cast.PostCastRequest")
    def test_cast_once_ok(self, mock_cast_request: MagicMock):
        mana_left = 11.1
        mock_cast_request.return_value = MockCastRequest(success=True,
                                                         remaining_user_mana=mana_left)
        spell_name = "intimidate"

        runner = CliRunner()
        result: Result = runner.invoke(cast, [spell_name])

        expected_spell = Spell(spell_name)
        mock_cast_request.assert_called_with(spell=expected_spell)

        expected_output = f"{spell_name} casted successfully: {mana_left:.1f} mana left.\n"
        assert result.stdout == expected_output

        assert result.exit_code == 0

    @patch("hopla.cli.cast.PostCastRequest")
    def test_cast_once_fail(self, mock_cast_request: MagicMock):
        err_msg = "Not enough mana."
        error_name = "NotAuthorized"
        mock_cast_request.return_value = MockCastRequest(
            success=False, message=err_msg, error=error_name,
            status_code=400
            # Yes, I know..., but according to the docs 400 is returned with NotAuthorized:
            # https://habitica.com/apidoc/#api-User-UserCast
        )

        spell_name = "protectAura"

        runner = CliRunner()
        result: Result = runner.invoke(cast, [spell_name])

        expected_spell = Spell(spell_name)
        mock_cast_request.assert_called_with(spell=expected_spell)

        assert '"success": false' in result.stdout
        assert f'"message": "{err_msg}"' in result.stdout
        assert f'"error": "{error_name}"' in result.stdout

        assert result.exit_code == 1


class TestCastHelpers:
    @pytest.mark.parametrize("spell_name,remaining_mana,expected_times", [
        ("toolsOfTrade", 97., 3),
        ("toolsOfTrade", 101., 4),
        ("healAll", 101., 4),
        ("earth", 69., 1),
        ("earth", 71.2, 2),
        ("stealth", 1.2, 0),
        ("defensiveStance", 50.0, 2)
    ])
    def test_times_until_out_of_mana(self,
                                     spell_name: str,
                                     remaining_mana: float,
                                     expected_times: int):
        spell = Spell(name=spell_name)
        result_times: int = times_until_out_of_mana(spell, remaining_mana=remaining_mana)
        assert result_times == expected_times
