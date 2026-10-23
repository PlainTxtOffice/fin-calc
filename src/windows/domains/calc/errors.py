"""Domain error types for the calculator."""


class EvaluationError(Exception):
    """Raised when an expression cannot be evaluated.

    Covers division by zero, log of non-positive values,
    mismatched parentheses, and invalid token sequences.
    """
