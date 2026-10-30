"""Tokenize complete text expressions without silently dropping input."""

from __future__ import annotations

import re

from fin_calc.domains.calc.errors import EvaluationError

MAX_EXPRESSION_LENGTH = 2048
MAX_EXPRESSION_TOKENS = 128
_TOKEN = re.compile(
    r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
    r"|log\b|[+*/^()\-]",
)


def parse_expression(expression: str) -> list[str]:
    """Return evaluator tokens, rejecting unknown input and excessive size.

    Whitespace separates tokens; it never joins numeric fragments. Limits
    bound the recursive evaluator's input for interactive text entry.
    """
    if len(expression) > MAX_EXPRESSION_LENGTH:
        msg = f"Expression exceeds {MAX_EXPRESSION_LENGTH} characters"
        raise EvaluationError(msg)
    tokens: list[str] = []
    position = 0
    while position < len(expression):
        if expression[position].isspace():
            position += 1
            continue
        match = _TOKEN.match(expression, position)
        if match is None:
            msg = f"Invalid input at character {position + 1}"
            raise EvaluationError(msg)
        tokens.append(match[0])
        if len(tokens) > MAX_EXPRESSION_TOKENS:
            msg = f"Expression exceeds {MAX_EXPRESSION_TOKENS} tokens"
            raise EvaluationError(msg)
        position = match.end()
    return tokens
