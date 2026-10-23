"""Presentation-only formatting for calculator results."""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, InvalidOperation
from decimal import Decimal as D

MAX_DECIMAL_PLACES = 6


def format_result(value_str: str, decimal_places: int | None) -> str:
    """Round a result string for display without touching stored values.

    Parameters
    ----------
    value_str : str
        The full-precision Decimal result as a string.
    decimal_places : int | None
        Number of decimal places to show, or None for full precision.

    Returns
    -------
    str
        The rounded string, or ``value_str`` unchanged when
        ``decimal_places`` is None or the value cannot be quantized.

    """
    if decimal_places is None:
        return value_str
    try:
        value = D(value_str)
        quantum = D(1).scaleb(-decimal_places)
        return str(value.quantize(quantum, rounding=ROUND_HALF_EVEN))
    except InvalidOperation:
        return value_str
