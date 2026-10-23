"""Tests for presentation-only result formatting."""

from __future__ import annotations

from src.windows.domains.calc.formatting import format_result


class TestFormatResult:
    """Tests for format_result."""

    def test_none_returns_unchanged(self):
        assert format_result("3.14159", None) == "3.14159"

    def test_rounds_to_places(self):
        assert format_result("3.14159", 2) == "3.14"

    def test_rounds_half_even(self):
        assert format_result("2.5", 0) == "2"
        assert format_result("3.5", 0) == "4"

    def test_pads_shorter_values(self):
        assert format_result("2", 2) == "2.00"

    def test_zero_places_drops_fraction(self):
        assert format_result("7.9", 0) == "8"

    def test_non_numeric_returned_unchanged(self):
        assert format_result("oops", 2) == "oops"

    def test_huge_exponent_returned_unchanged(self):
        # quantize on a value like 1E+100 raises InvalidOperation;
        # the helper must fall back to the raw string.
        assert format_result("1E+100", 2) == "1E+100"
