from __future__ import annotations


class APIError(Exception):
    """Base exception for API-domain errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NodeAlreadyExistsError(APIError):
    def __init__(self, node_name: str) -> None:
        super().__init__(f"Node '{node_name}' already exists", status_code=409)


class NodeNotFoundError(APIError):
    def __init__(self, node_name: str) -> None:
        super().__init__(f"Node '{node_name}' was not found", status_code=404)


class MetricsNotAvailableError(APIError):
    def __init__(self) -> None:
        super().__init__("No metrics available", status_code=404)
