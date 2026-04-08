"""Tests for the quantiles module (tokens → level 0-4)."""

from __future__ import annotations

from snake_tokscale.quantiles import compute_levels


class TestComputeLevels:
    def test_empty_dict_returns_empty(self):
        assert compute_levels({}) == {}

    def test_all_equal_values_return_level_one(self):
        tokens = {"2026-01-01": 100, "2026-01-02": 100, "2026-01-03": 100}
        assert compute_levels(tokens) == {
            "2026-01-01": 1,
            "2026-01-02": 1,
            "2026-01-03": 1,
        }

    def test_zero_days_stay_level_zero(self):
        tokens = {"a": 0, "b": 0, "c": 100, "d": 200, "e": 300, "f": 400}
        levels = compute_levels(tokens)
        assert levels["a"] == 0
        assert levels["b"] == 0
        assert levels["c"] >= 1

    def test_levels_are_monotone(self):
        tokens = {f"d{i}": i for i in range(1, 101)}
        levels = compute_levels(tokens)
        previous = 0
        for i in range(1, 101):
            lvl = levels[f"d{i}"]
            assert 1 <= lvl <= 4
            assert lvl >= previous
            previous = lvl

    def test_highest_value_is_level_four(self):
        tokens = {f"d{i}": i for i in range(1, 101)}
        levels = compute_levels(tokens)
        assert levels["d100"] == 4

    def test_only_nonzero_values_drive_quantiles(self):
        # Many zero days shouldn't drag quantile thresholds down.
        tokens = {f"z{i}": 0 for i in range(50)}
        tokens.update({f"v{i}": i * 10 for i in range(1, 11)})
        levels = compute_levels(tokens)
        assert all(levels[f"z{i}"] == 0 for i in range(50))
        assert levels["v10"] == 4
