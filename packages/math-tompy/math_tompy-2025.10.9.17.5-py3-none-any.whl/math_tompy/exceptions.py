class BaseMathException(Exception):
    """Base exception for math project."""


class EmptyListError(BaseMathException):
    """Raise when a list is found to be empty"""


class ExpressionTypeUnsupportedError(BaseMathException):
    """Raise when encountering a type that is not supported."""
