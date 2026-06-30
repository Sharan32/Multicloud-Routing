from __future__ import annotations


class ExecutorError(Exception):
    """Base class for executor errors."""


class InvalidRouteError(ExecutorError):
    """Raised when a route decision targets an unsupported route."""


class ExecutorFailureError(ExecutorError):
    """Raised when the underlying execution adapter fails."""
