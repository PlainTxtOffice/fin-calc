"""Exercise complete text input through the existing Decimal evaluator."""

from decimal import Decimal

import pytest

from src.windows.domains.calc.errors import EvaluationError
from src.windows.domains.calc.evaluator import evaluate
from src.windows.domains.calc.parsing import parse_expression


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("0.1 + 0.2", "0.3"),
        ("2*(3+4)", "14"),
        ("log(100)", "2"),
        ("2^3^2", "512"),
        ("-2 ^ 2", "4"),
        ("2*-3", "-6"),
        ("1e-3 + .5", "0.501"),
    ],
)
def test_text_evaluates_with_decimal_rules(text, expected):
    assert evaluate(parse_expression(text)) == Decimal(expected)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "1 2",
        "1..2",
        "1+garbage",
        "2**3",
        "2(3)",
        "NaN",
        "Infinity",
        "1,000",
        "(2+3",
        "1/0",
        "log(0)",
        "9" * 2049,
        "(" * 129 + "1" + ")" * 129,
    ],
)
def test_bad_input_is_rejected_without_dropping_characters(text):
    with pytest.raises(EvaluationError):
        evaluate(parse_expression(text))
