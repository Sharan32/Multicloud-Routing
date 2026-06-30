from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from router.models import RouteHistoryEntry


class HistoryStore:
    """Persistence abstraction for routing decision history."""

    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: RouteHistoryEntry) -> None:
        records = self.read_all()
        records.append(entry)
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump([self._serialize(record) for record in records], handle, indent=2)

    def read_all(self) -> list[RouteHistoryEntry]:
        if not self.storage_path.exists():
            return []
        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []
        return [self._deserialize(item) for item in data if isinstance(item, dict)]

    def _serialize(self, entry: RouteHistoryEntry) -> dict[str, Any]:
        return {
            "timestamp": entry.timestamp,
            "old_route": entry.old_route,
            "new_route": entry.new_route,
            "reason": entry.reason,
            "old_score": entry.old_score,
            "new_score": entry.new_score,
        }

    def _deserialize(self, payload: dict[str, Any]) -> RouteHistoryEntry:
        return RouteHistoryEntry(
            timestamp=str(payload.get("timestamp", "")),
            old_route=payload.get("old_route"),
            new_route=str(payload.get("new_route", "")),
            reason=str(payload.get("reason", "")),
            old_score=payload.get("old_score"),
            new_score=float(payload.get("new_score", 0.0)),
        )
