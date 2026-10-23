"""Recursive descent evaluator over Decimal values.

Precedence (low to high):
    addition / subtraction
    multiplication / division
    exponentiation (right-associative)
    unary minus
    functions (log)
    parentheses

Unary minus deliberately binds tighter than ``^`` (Excel-style), so
``-2 ^ 2`` means ``(-2) ^ 2 = 4``. This matches the expression builder,
which folds a negation sign into the number token itself.
"""

from __future__ import annotations

import logging
from decimal import Decimal as D
from decimal import InvalidOperation

from src.windows.domains.calc.errors import EvaluationError

logger = logging.getLogger(__name__)


def evaluate(tokens: list[str]) -> D:
    """Evaluate a token list and return a Decimal result.

    Parameters
    ----------
    tokens : list[str]
        Symbols from ExpressionBuilder.symbol_list().

    Returns
    -------
    Decimal
        The computed result.

    Raises
    ------
    EvaluationError
        On invalid expressions, division by zero, or log domain errors.

    """
    if not tokens:
        msg = "Empty expression"
        raise EvaluationError(msg)
    parser = _Parser(tokens)
    try:
        result = parser.parse_expression()
    except ArithmeticError as err:
        logger.debug("Decimal arithmetic trap: %r", err)
        msg = "Result out of range"
        raise EvaluationError(msg) from err
    if parser.pos < len(parser.tokens):
        msg = "Unexpected token after expression"
        raise EvaluationError(msg)
    if not result.is_finite():
        msg = "Result out of range"
        raise EvaluationError(msg)
    return result


class _Parser:
    """Recursive descent parser for Decimal arithmetic."""

    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> str | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self) -> str:
        symbol = self.tokens[self.pos]
        self.pos += 1
        return symbol

    def parse_expression(self) -> D:
        """Parse addition and subtraction (lowest precedence)."""
        left = self._parse_term()
        while self._peek() in {"+", "-"}:
            op = self._consume()
            right = self._parse_term()
            left = left + right if op == "+" else left - right
        return left

    def _parse_term(self) -> D:
        """Parse multiplication and division."""
        left = self._parse_exponent()
        while self._peek() in {"*", "/"}:
            op = self._consume()
            right = self._parse_exponent()
            if op == "*":
                left *= right
            else:
                if right == 0:
                    msg = "Division by zero"
                    raise EvaluationError(msg)
                left /= right
        return left

    def _parse_exponent(self) -> D:
        """Parse exponentiation (right-associative)."""
        base = self._parse_unary()
        if self._peek() == "^":
            self._consume()
            exp = self._parse_exponent()
            try:
                return base**exp
            except InvalidOperation as err:
                msg = f"Invalid exponentiation: {base} ^ {exp}"
                raise EvaluationError(
                    msg,
                ) from err
        return base

    def _parse_unary(self) -> D:
        """Parse unary minus."""
        if self._peek() == "-":
            self._consume()
            return -self._parse_primary()
        return self._parse_primary()

    def _parse_primary(self) -> D:
        """Parse numbers, parenthesised expressions, and functions."""
        current = self._peek()
        if current is None:
            msg = "Unexpected end of expression"
            raise EvaluationError(msg)

        if current == "log":
            return self._parse_log()

        if current == "(":
            self._consume()
            result = self.parse_expression()
            if self._peek() != ")":
                msg = "Mismatched parentheses"
                raise EvaluationError(msg)
            self._consume()
            return result

        return self._parse_number()

    def _parse_log(self) -> D:
        """Parse log(expression) as base-10 logarithm."""
        self._consume()  # consume "log"
        if self._peek() != "(":
            msg = "Expected '(' after log"
            raise EvaluationError(msg)
        self._consume()  # consume "("
        value = self.parse_expression()
        if self._peek() != ")":
            msg = "Mismatched parentheses in log"
            raise EvaluationError(msg)
        self._consume()  # consume ")"

        if value <= 0:
            logger.debug("Log of non-positive value: %s", value)
            msg = "Log undefined for non-positive values"
            raise EvaluationError(
                msg,
            )
        return value.ln() / D(10).ln()

    def _parse_number(self) -> D:
        """Parse a numeric literal."""
        raw = self._consume()
        try:
            return D(raw)
        except InvalidOperation as err:
            msg = f"Invalid number: {raw}"
            raise EvaluationError(msg) from err
