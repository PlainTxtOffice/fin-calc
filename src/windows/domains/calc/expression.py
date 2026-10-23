"""Expression builder for the calculator domain.

Manages a token list, validates input sequences, and produces
a display string and token list for the evaluator.
"""

from __future__ import annotations

import string
from decimal import Decimal as D
from decimal import InvalidOperation

OPERATORS = {"+", "-", "*", "/", "^"}
DIGITS = set(string.digits)


class ExpressionBuilder:
    """Build a mathematical expression token by token with validation.

    Tracks tokens as a list of strings. Numbers are accumulated as
    a single token. Operators, parentheses, and functions are
    individual tokens.
    """

    def __init__(self) -> None:
        """Initialize an empty expression builder state."""
        self.tokens: list[str] = []
        self._open_parens: int = 0
        self._result_pending: bool = False

    def add_symbol(self, symbol: str) -> bool:
        """Append a symbol if it forms a valid sequence.

        Returns
        -------
        bool
            True if the symbol was accepted, False if rejected.

        """
        if self._result_pending and not self._continue_from_result(symbol):
            return False
        before = len(self.tokens)
        snapshot = self.tokens[-1] if self.tokens else None
        if symbol in DIGITS or symbol == ".":
            self._add_digit_or_dot(symbol)
        elif symbol in OPERATORS:
            self._add_operator(symbol)
        elif symbol == "(":
            self._add_open_paren()
        elif symbol == ")":
            self._add_close_paren()
        elif symbol == "log":
            self._add_function(symbol)
        else:
            return False
        after = self.tokens[-1] if self.tokens else None
        return len(self.tokens) != before or snapshot != after

    def clear(self) -> None:
        """Remove all tokens."""
        self.tokens.clear()
        self._open_parens = 0
        self._result_pending = False

    def clear_entry(self) -> None:
        """Remove the last complete token."""
        self._result_pending = False
        if not self.tokens:
            return
        removed = self.tokens.pop()
        if removed == "(":
            self._open_parens -= 1
        elif removed == ")":
            self._open_parens += 1

    def backspace(self) -> None:
        """Remove the last character of the current number token."""
        self._result_pending = False
        if not self.tokens:
            return
        last = self.tokens[-1]
        if last in OPERATORS or last in {"(", ")", "log"}:
            self.clear_entry()
            return
        if len(last) == 1:
            self.tokens.pop()
        else:
            self.tokens[-1] = last[:-1]

    def toggle_sign(self) -> None:
        """Toggle the sign of the current number being entered."""
        if not self.tokens:
            return
        last = self.tokens[-1]
        if last in OPERATORS or last in {"(", ")", "log"}:
            return
        if last.startswith("-"):
            self.tokens[-1] = last[1:]
        else:
            self.tokens[-1] = "-" + last

    def insert_result(self, result: str) -> None:
        """Insert a previous result value as a number token.

        The inserted token is sealed: digits never merge into it. When it
        is the only token, a following digit starts a fresh expression.
        """
        if self.tokens and self._last_is_number():
            return
        self.tokens.append(result)
        self._result_pending = True

    def _continue_from_result(self, symbol: str) -> bool:
        """Resolve a pending result token before accepting ``symbol``.

        Returns
        -------
        bool
            True if add_symbol should proceed, False to reject the symbol.

        """
        self._result_pending = False
        starts_operand = symbol in DIGITS or symbol in {".", "(", "log"}
        if not starts_operand:
            return True
        if len(self.tokens) == 1:
            self.clear()
            return True
        return False

    def to_display(self) -> str:
        """Format the token list for display."""
        if not self.tokens:
            return ""
        return self._format_display()

    def symbol_list(self) -> list[str]:
        """Return a copy of the symbol list for the evaluator."""
        return list(self.tokens)

    def _add_digit_or_dot(self, char: str) -> None:
        if char == "." and self.tokens and "." in self.tokens[-1]:
            return
        if self.tokens and self.tokens[-1] in {")", "log"}:
            return
        if (self.tokens and self._is_number(self.tokens[-1])) or (
            self.tokens and self.tokens[-1] == "-" and self._is_negation()
        ):
            self.tokens[-1] += char
        elif char == ".":
            self.tokens.append("0.")
        else:
            self.tokens.append(char)

    def _is_negation(self) -> bool:
        """Check if the trailing lone '-' is a negation prefix."""
        if not self.tokens or self.tokens[-1] != "-":
            return False
        if len(self.tokens) == 1:
            return True
        prev = self.tokens[-2]
        return prev in OPERATORS or prev in {"(", "log"}

    def _add_operator(self, op: str) -> None:
        if not self.tokens:
            if op == "-":
                self.tokens.append("-")
            return
        last = self.tokens[-1]
        if last == "-" and self._is_negation():
            return
        if last in OPERATORS or last in {"(", "log"}:
            if op == "-":
                self.tokens.append("-")
            return
        self.tokens.append(op)

    def _add_open_paren(self) -> None:
        if self.tokens and (self._last_is_number() or self.tokens[-1] == ")"):
            return
        self.tokens.append("(")
        self._open_parens += 1

    def _add_close_paren(self) -> None:
        if self._open_parens <= 0:
            return
        if (
            not self.tokens
            or self.tokens[-1] in OPERATORS
            or self.tokens[-1] == "("
        ):
            return
        self.tokens.append(")")
        self._open_parens -= 1

    def _add_function(self, name: str) -> None:
        if self.tokens and (self._last_is_number() or self.tokens[-1] == ")"):
            return
        self.tokens.append(name)

    def _last_is_number(self) -> bool:
        if not self.tokens:
            return False
        return self._is_number(self.tokens[-1])

    @staticmethod
    def _is_number(value: str) -> bool:
        if not any(c in DIGITS for c in value):
            return False
        try:
            D(value)
        except InvalidOperation:
            return False
        return True

    def _format_display(self) -> str:
        parts: list[str] = []
        for i, sym in enumerate(self.tokens):
            if i > 0 and not (
                self._is_number(self.tokens[i - 1]) and self._is_number(sym)
            ):
                parts.append(" ")
            parts.append(sym)
        return "".join(parts)
