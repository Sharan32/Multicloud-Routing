from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExecutionHistoryEntry:
    """Represents one execution action taken by the engine."""

    timestamp: str
    route: str
    reason: str
    executed: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "route": self.route,
            "reason": self.reason,
            "executed": self.executed,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ExecutionHistoryEntry":
        return cls(
            timestamp=payload["timestamp"],
            route=payload["route"],
            reason=payload["reason"],
            executed=bool(payload["executed"]),
        )


class ExecutionHistoryStore:
    """Persists execution history entries."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_all(self) -> list[ExecutionHistoryEntry]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return [ExecutionHistoryEntry.from_payload(item) for item in payload]

    def append(self, entry: ExecutionHistoryEntry) -> None:
        records = self.read_all()
        records.append(entry)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump([record.to_payload() for record in records], handle, indent=2)
