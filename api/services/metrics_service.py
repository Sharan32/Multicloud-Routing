from __future__ import annotations

from typing import Any

from api.exceptions import MetricsNotAvailableError
from api.repositories.metrics_repository import MetricsRepository


class MetricsService:
    """Service for retrieving monitoring metrics."""

    def __init__(self, repository: MetricsRepository) -> None:
        self.repository = repository

    def get_latest_metrics(self) -> dict[str, Any] | None:
        return self.repository.get_latest_metrics()

    def get_all_metrics(self) -> list[dict[str, Any]]:
        metrics = self.repository.read_metrics()
        if not metrics:
            raise MetricsNotAvailableError()
        return metrics
