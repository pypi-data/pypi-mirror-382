class BaseVectorException(Exception):
    """Base exception for Vector project."""


class EmptyIterableError(BaseVectorException):
    """Raise when an iterable is found to be empty."""


class NoLinesIntersectionError(BaseVectorException):
    """Raise when none of the calculated lines intersect."""


class UnexpectedUnpredictableError(BaseVectorException):
    """Raise when if-else should have covered all cases, but something yet unknown circumvents first guards."""
