from hopla.cli.groupcmds.buy import times_until_poor


class TestTimesUntilPoor:
    def test_times_until_poor__budget_is0(self):
        assert times_until_poor(0.) == 0

    def test_times_until_poor__budget_is_below100(self):
        assert times_until_poor(92.3) == 0

    def test_times_until_poor__budget_is_over100(self):
        assert times_until_poor(212) == 2
