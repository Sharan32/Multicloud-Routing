from __future__ import annotations


class RoutingError(Exception):
    """Base exception for routing errors."""


class NoMetricsAvailableError(RoutingError):
    """Raised when no metrics are available for routing."""


class NoHealthyNodeError(RoutingError):
    """Raised when no node passes health thresholds."""


class RoutingFailureError(RoutingError):
    """Raised when routing cannot complete successfully."""
