from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class MetricsStore(Protocol):
    """Storage abstraction for metric persistence."""

    def read_metrics(self) -> list[dict[str, Any]]: ...

    def write_metrics(self, metrics: dict[str, Any]) -> None: ...


class MetricsRepository:
    """Repository for reading and writing monitoring metrics from disk."""

    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def read_metrics(self) -> list[dict[str, Any]]:
        if not self.storage_path.exists():
            return []

        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []

        if isinstance(data, list):
            return data
        return []

    def write_metrics(self, metrics: dict[str, Any]) -> None:
        existing = self.read_metrics()
        existing.append(metrics)
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(existing, handle, indent=2)

    def get_latest_metrics(self) -> dict[str, Any] | None:
        metrics = self.read_metrics()
        if not metrics:
            return None
        return metrics[-1]
