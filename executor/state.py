from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExecutionState:
    """Persistent execution state for the active route."""

    active_route: str | None = None
    last_switch_at: datetime | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "active_route": self.active_route,
            "last_switch_at": self.last_switch_at.isoformat() if self.last_switch_at else None,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ExecutionState":
        last_switch_at = payload.get("last_switch_at")
        return cls(
            active_route=payload.get("active_route"),
            last_switch_at=datetime.fromisoformat(last_switch_at) if last_switch_at else None,
        )


class RouteStateStore:
    """Persists the execution engine state to disk."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def default_state(self, active_route: str | None = None, last_switch_at: datetime | None = None) -> ExecutionState:
        return ExecutionState(active_route=active_route, last_switch_at=last_switch_at)

    def read(self) -> ExecutionState:
        if not self.path.exists():
            return self.default_state()
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return ExecutionState.from_payload(payload)

    def save(self, state: ExecutionState) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(state.to_payload(), handle, indent=2)
