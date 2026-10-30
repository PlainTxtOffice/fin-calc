"""Tests for the calculator expression builder."""

from fin_calc.domains.calc.expression import ExpressionBuilder


class TestExpressionBuilderBasic:
    """Tests for basic token management."""

    def test_empty_expression(self):
        builder = ExpressionBuilder()
        assert builder.tokens == []
        assert builder.to_display() == ""

    def test_add_digit(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        assert builder.to_display() == "5"

    def test_add_multi_digit_number(self):
        builder = ExpressionBuilder()
        builder.add_symbol("1")
        builder.add_symbol("2")
        builder.add_symbol("3")
        assert builder.to_display() == "123"

    def test_add_decimal_point(self):
        builder = ExpressionBuilder()
        builder.add_symbol("3")
        builder.add_symbol(".")
        builder.add_symbol("1")
        builder.add_symbol("4")
        assert builder.to_display() == "3.14"

    def test_add_operator_after_number(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("+")
        builder.add_symbol("3")
        assert builder.to_display() == "5 + 3"

    def test_clear_all(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("+")
        builder.clear()
        assert builder.tokens == []
        assert builder.to_display() == ""

    def test_clear_entry(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("+")
        builder.add_symbol("3")
        builder.clear_entry()
        assert builder.to_display() == "5 +"

    def test_backspace_digit(self):
        builder = ExpressionBuilder()
        builder.add_symbol("1")
        builder.add_symbol("2")
        builder.backspace()
        assert builder.to_display() == "1"

    def test_backspace_empty(self):
        builder = ExpressionBuilder()
        builder.backspace()
        assert builder.to_display() == ""


class TestExpressionBuilderValidation:
    """Tests for input validation rules."""

    def test_subtraction(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("-")
        builder.add_symbol("3")
        assert builder.to_display() == "5 - 3"

    def test_reject_operator_at_start(self):
        builder = ExpressionBuilder()
        builder.add_symbol("+")
        assert builder.to_display() == ""

    def test_reject_multiply_at_start(self):
        builder = ExpressionBuilder()
        builder.add_symbol("*")
        assert builder.to_display() == ""

    def test_reject_consecutive_operators(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("+")
        builder.add_symbol("*")
        assert builder.to_display() == "5 +"

    def test_reject_double_decimal(self):
        builder = ExpressionBuilder()
        builder.add_symbol("3")
        builder.add_symbol(".")
        builder.add_symbol(".")
        assert builder.to_display() == "3."

    def test_allow_negative_at_start(self):
        builder = ExpressionBuilder()
        builder.add_symbol("-")
        builder.add_symbol("5")
        assert builder.to_display() == "-5"

    def test_allow_negative_after_operator(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("+")
        builder.add_symbol("-")
        builder.add_symbol("3")
        assert builder.to_display() == "5 + -3"

    def test_allow_negative_after_open_paren(self):
        builder = ExpressionBuilder()
        builder.add_symbol("(")
        builder.add_symbol("-")
        builder.add_symbol("5")
        builder.add_symbol(")")
        assert builder.to_display() == "( -5 )"


class TestExpressionBuilderParentheses:
    """Tests for parentheses handling."""

    def test_open_paren(self):
        builder = ExpressionBuilder()
        builder.add_symbol("(")
        builder.add_symbol("3")
        builder.add_symbol("+")
        builder.add_symbol("2")
        builder.add_symbol(")")
        assert builder.to_display() == "( 3 + 2 )"

    def test_nested_parens(self):
        builder = ExpressionBuilder()
        for sym in ["(", "(", "1", "+", "2", ")", "*", "3", ")"]:
            builder.add_symbol(sym)
        assert builder.to_display() == "( ( 1 + 2 ) * 3 )"

    def test_reject_close_paren_without_open(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol(")")
        assert builder.to_display() == "5"

    def test_reject_number_after_close_paren(self):
        builder = ExpressionBuilder()
        for sym in ["(", "1", ")"]:
            builder.add_symbol(sym)
        accepted = builder.add_symbol("2")
        assert accepted is False
        assert builder.to_display() == "( 1 )"

    def test_reject_open_paren_after_close_paren(self):
        builder = ExpressionBuilder()
        for sym in ["(", "1", ")"]:
            builder.add_symbol(sym)
        accepted = builder.add_symbol("(")
        assert accepted is False
        assert builder.to_display() == "( 1 )"


class TestExpressionBuilderFunctions:
    """Tests for log and exponent tokens."""

    def test_add_log(self):
        builder = ExpressionBuilder()
        builder.add_symbol("log")
        builder.add_symbol("(")
        builder.add_symbol("1")
        builder.add_symbol("0")
        builder.add_symbol(")")
        assert builder.to_display() == "log ( 10 )"

    def test_reject_number_after_log(self):
        builder = ExpressionBuilder()
        builder.add_symbol("log")
        accepted = builder.add_symbol("1")
        assert accepted is False
        assert builder.to_display() == "log"

    def test_add_exponent(self):
        builder = ExpressionBuilder()
        builder.add_symbol("2")
        builder.add_symbol("^")
        builder.add_symbol("3")
        assert builder.to_display() == "2 ^ 3"


class TestExpressionBuilderToggleSign:
    """Tests for +/- sign toggle."""

    def test_toggle_positive_to_negative(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.toggle_sign()
        assert builder.to_display() == "-5"

    def test_toggle_negative_to_positive(self):
        builder = ExpressionBuilder()
        builder.add_symbol("-")
        builder.add_symbol("5")
        builder.toggle_sign()
        assert builder.to_display() == "5"

    def test_toggle_sign_no_number(self):
        builder = ExpressionBuilder()
        builder.toggle_sign()
        assert builder.to_display() == ""


class TestExpressionBuilderInsertResult:
    """Tests for inserting a previous result."""

    def test_insert_result_into_empty(self):
        builder = ExpressionBuilder()
        builder.insert_result("42")
        assert builder.to_display() == "42"

    def test_insert_result_after_operator(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("+")
        builder.insert_result("10")
        assert builder.to_display() == "5 + 10"


class TestExpressionBuilderResultContinuation:
    """After ``=`` an operator continues from the result, a digit starts over."""

    def test_digit_after_result_starts_fresh(self):
        builder = ExpressionBuilder()
        builder.insert_result("5")
        builder.add_symbol("3")
        assert builder.to_display() == "3"

    def test_dot_after_result_starts_fresh(self):
        builder = ExpressionBuilder()
        builder.insert_result("5")
        builder.add_symbol(".")
        assert builder.to_display() == "0."

    def test_operator_after_result_continues(self):
        builder = ExpressionBuilder()
        builder.insert_result("5")
        builder.add_symbol("+")
        builder.add_symbol("3")
        assert builder.to_display() == "5 + 3"

    def test_open_paren_after_result_starts_fresh(self):
        builder = ExpressionBuilder()
        builder.insert_result("5")
        builder.add_symbol("(")
        assert builder.to_display() == "("

    def test_log_after_result_starts_fresh(self):
        builder = ExpressionBuilder()
        builder.insert_result("5")
        builder.add_symbol("log")
        assert builder.to_display() == "log"

    def test_second_result_insert_after_scientific_result_is_blocked(self):
        builder = ExpressionBuilder()
        builder.insert_result("1E-30")
        builder.insert_result("42")
        assert builder.symbol_list() == ["1E-30"]

    def test_scientific_result_spacing_in_display(self):
        builder = ExpressionBuilder()
        builder.insert_result("1E-30")
        builder.add_symbol("+")
        builder.add_symbol("2")
        assert builder.to_display() == "1E-30 + 2"

    def test_toggle_sign_on_scientific_result(self):
        builder = ExpressionBuilder()
        builder.insert_result("1E-30")
        builder.toggle_sign()
        assert builder.to_display() == "-1E-30"

    def test_digit_never_merges_into_mid_expression_result(self):
        builder = ExpressionBuilder()
        builder.add_symbol("5")
        builder.add_symbol("+")
        builder.insert_result("10")
        accepted = builder.add_symbol("3")
        assert accepted is False
        assert builder.to_display() == "5 + 10"
