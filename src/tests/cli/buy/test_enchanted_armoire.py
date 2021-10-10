from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner, Result

from hopla.cli.buy.enchanted_armoire import get_buy_times_within_budget, \
    times_until_out_of_gp, enchanted_armoire
from hopla.cli.groupcmds.get_user import HabiticaUser
from tests.testutils.user_test_utils import UserTestUtil


class TestTimesUntilPoor:
    def test_times_until_out_of_gp_budget_is0(self):
        assert times_until_out_of_gp(0.) == 0

    def test_times_until_out_of_gp_budget_is_below100(self):
        assert times_until_out_of_gp(92.3) == 0

    def test_times_until_out_of_gp_budget_is_over100(self):
        assert times_until_out_of_gp(212) == 2


class TestBuyTimesWithBudget:

    @pytest.mark.parametrize(
        "gold,expected_buy_times", [(550.1, 5), (5., 0), (69., 0), (9000.1, 90)]
    )
    def test_get_buy_times_within_budget_out_of_gp(self, gold: float,
                                                   expected_buy_times: int):
        user: HabiticaUser = UserTestUtil.user_with_gp(gold=gold)

        times: int = get_buy_times_within_budget(user=user,
                                                 until_out_of_gp_flag=True,
                                                 requested_times=None)

        assert times == expected_buy_times

    @pytest.mark.parametrize(
        "gold,requested_times,expected_times",
        [(550.1, 5, 5),
         (550.1, 4, 4),
         (5., 1, 0),  # cannot buy 1 time with 5gp
         (700.1, None, 1),  # when requested_times is None, use 1
         (705.5, 9, 7),  # cannot buy 9 times with 705.5 gp
         (742., 4, 4),
         (9000.1, 42, 42)]
    )
    def test_get_buy_times_within_budget_with_times(self, gold: float,
                                                    requested_times,
                                                    expected_times: int):
        user: HabiticaUser = UserTestUtil.user_with_gp(gold=gold)

        times: int = get_buy_times_within_budget(user=user,
                                                 until_out_of_gp_flag=False,
                                                 requested_times=requested_times)

        assert times == expected_times


class TestBuyEnchantedArmoireCliCommand:

    @patch("hopla.cli.buy.enchanted_armoire.BuyEnchantedArmoireRequest.post_buy_request")
    @patch("hopla.cli.buy.enchanted_armoire.HabiticaUserRequest.request_user_data_or_exit")
    def test_buy_enchanted_armoire_ok(self,
                                      user_request: MagicMock,
                                      buy_request: MagicMock):
        gold = 500.
        user_request.return_value = UserTestUtil.user_with_gp(gold=gold)

        class MockBuyResponse:
            def __init__(self, json):
                self._json = json

            def json(self) -> dict:
                return self._json

        exp = 35
        armoire_value = {"type": "experience", "value": exp}
        json_response = {
            "success": True,
            "message": "You wrestle with the Armoire and gain Experience. Take that!",
            "data": {
                "armoire": armoire_value
            }
        }
        buy_request.return_value = MockBuyResponse(json=json_response)

        runner = CliRunner()
        result: Result = runner.invoke(enchanted_armoire)

        assert result.exit_code == 0
        assert '"type": "experience",' in result.stdout
        assert f'"value": {exp}' in result.stdout

    def test_buy_enchanted_armoire_times_and_until_out_of_gp_conflict_fail(self):
        runner = CliRunner()
        result: Result = runner.invoke(enchanted_armoire, ["--times", 10, "--until-out-of-gp"])

        expected_msg = "Error: --times and --until-out-of-gp are mutually exclusive.\n"
        assert result.stdout.endswith(expected_msg)
        assert result.exit_code == 2
