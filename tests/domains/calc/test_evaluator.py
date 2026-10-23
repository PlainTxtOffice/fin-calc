"""Tests for the calculator expression evaluator."""

from decimal import Decimal

import pytest

from src.windows.domains.calc.errors import EvaluationError
from src.windows.domains.calc.evaluator import evaluate


class TestEvaluatorArithmetic:
    """Tests for basic arithmetic operations."""

    def test_add(self):
        assert evaluate(["3", "+", "2"]) == Decimal("5")

    def test_subtract(self):
        assert evaluate(["10", "-", "4"]) == Decimal("6")

    def test_multiply(self):
        assert evaluate(["3", "*", "7"]) == Decimal("21")

    def test_divide(self):
        assert evaluate(["15", "/", "4"]) == Decimal("3.75")

    def test_single_number(self):
        assert evaluate(["42"]) == Decimal("42")

    def test_negative_number(self):
        assert evaluate(["-5", "+", "3"]) == Decimal("-2")

    def test_decimal_precision(self):
        result = evaluate(["0.1", "+", "0.2"])
        assert result == Decimal("0.3")


class TestEvaluatorPrecedence:
    """Tests for operator precedence."""

    def test_multiply_before_add(self):
        assert evaluate(["2", "+", "3", "*", "4"]) == Decimal("14")

    def test_divide_before_subtract(self):
        assert evaluate(["10", "-", "6", "/", "2"]) == Decimal("7")

    def test_exponent_before_multiply(self):
        assert evaluate(["2", "^", "3", "*", "4"]) == Decimal("32")

    def test_left_to_right_same_precedence(self):
        assert evaluate(["10", "-", "3", "-", "2"]) == Decimal("5")


class TestEvaluatorParentheses:
    """Tests for parentheses grouping."""

    def test_parens_override_precedence(self):
        assert evaluate(["(", "2", "+", "3", ")", "*", "4"]) == Decimal("20")

    def test_nested_parens(self):
        result = evaluate(["(", "(", "1", "+", "2", ")", "*", "3", ")"])
        assert result == Decimal("9")

    def test_parens_with_exponent(self):
        assert evaluate(["(", "2", "+", "1", ")", "^", "2"]) == Decimal("9")


class TestEvaluatorFunctions:
    """Tests for log base 10."""

    def test_log_10(self):
        assert evaluate(["log", "(", "10", ")"]) == Decimal("1")

    def test_log_100(self):
        assert evaluate(["log", "(", "100", ")"]) == Decimal("2")

    def test_log_1(self):
        assert evaluate(["log", "(", "1", ")"]) == Decimal("0")

    def test_log_in_expression(self):
        result = evaluate(["log", "(", "100", ")", "+", "3"])
        assert result == Decimal("5")


class TestEvaluatorExponent:
    """Tests for the ^ operator."""

    def test_power(self):
        assert evaluate(["2", "^", "10"]) == Decimal("1024")

    def test_power_zero(self):
        assert evaluate(["5", "^", "0"]) == Decimal("1")

    def test_power_one(self):
        assert evaluate(["7", "^", "1"]) == Decimal("7")


class TestEvaluatorSignPrecedence:
    """A leading minus binds to its operand, tighter than ^ (Excel-style).

    ``-2 ^ 2`` means ``(-2) ^ 2 = 4``. This matches how the builder folds
    the sign into the number token, so no parentheses are required.
    """

    def test_negative_literal_squared(self):
        assert evaluate(["-2", "^", "2"]) == Decimal("4")

    def test_unary_minus_before_parens_squared(self):
        result = evaluate(["-", "(", "2", ")", "^", "2"])
        assert result == Decimal("4")


class TestEvaluatorErrors:
    """Tests for error conditions."""

    def test_division_by_zero(self):
        with pytest.raises(EvaluationError, match="[Dd]ivision by zero"):
            evaluate(["5", "/", "0"])

    def test_log_of_zero(self):
        with pytest.raises(EvaluationError, match="[Ll]og"):
            evaluate(["log", "(", "0", ")"])

    def test_log_of_negative(self):
        with pytest.raises(EvaluationError, match="[Ll]og"):
            evaluate(["log", "(", "-5", ")"])

    def test_empty_expression(self):
        with pytest.raises(EvaluationError):
            evaluate([])

    def test_mismatched_parens(self):
        with pytest.raises(EvaluationError):
            evaluate(["(", "3", "+", "2"])

    def test_overflow_raises_evaluation_error(self):
        with pytest.raises(EvaluationError, match="[Oo]ut of range"):
            evaluate(["9", "^", "9999999"])

    def test_non_finite_result_raises_evaluation_error(self):
        with pytest.raises(EvaluationError, match="[Oo]ut of range"):
            evaluate(["0", "^", "-1"])

    def test_multiplication_overflow_raises_evaluation_error(self):
        with pytest.raises(EvaluationError, match="[Oo]ut of range"):
            evaluate(["9", "^", "999999", "*", "9", "^", "999999"])
