#!/usr/bin/env python3
import pytest
from click.testing import CliRunner, Result

from hopla.cli.get_user.stats import stats
from hopla.cli.groupcmds.get_user import HabiticaUser


class TestStatsCliCommand:
    MP = 213.1
    GP = 10.2
    LVL = 104

    def test_stats_all_ok(self, test_user: HabiticaUser):
        runner = CliRunner()

        result: Result = runner.invoke(stats, ["all"], obj=test_user)

        assert f'"mp": {TestStatsCliCommand.MP}' in result.stdout
        assert f'"gp": {TestStatsCliCommand.GP}' in result.stdout
        assert f'"lvl": {TestStatsCliCommand.LVL}' in result.stdout
        assert result.exit_code == 0

    def test_stats_all_same_as_no_arg_ok(self, test_user: HabiticaUser):
        runner = CliRunner()

        result_all: Result = runner.invoke(stats, ["all"], obj=test_user)
        result_no_arg: Result = runner.invoke(stats, obj=test_user)

        assert result_all.stdout == result_no_arg.stdout
        assert result_all.exit_code == result_no_arg.exit_code

    def test_stats_with_level_ok(self, test_user: HabiticaUser):
        runner = CliRunner()

        result_level: Result = runner.invoke(stats, ["level"], obj=test_user)

        assert result_level.stdout == f"{TestStatsCliCommand.LVL}\n"
        assert result_level.exit_code == 0

    @pytest.fixture
    def test_user(self) -> HabiticaUser:
        user_stats = {
            "mp": TestStatsCliCommand.MP,
            "gp": TestStatsCliCommand.GP,
            "lvl": TestStatsCliCommand.LVL
        }
        return HabiticaUser({
            "stats": user_stats,
            # contributor is just some extra data to make sure that we ignore this.
            "contributor": {"level": 3}}
        )
