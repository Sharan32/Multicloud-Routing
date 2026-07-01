from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict


@dataclass(slots=True)
class NetworkMetrics:
    """Represents a snapshot of remote node network health."""

    timestamp: datetime
    node: str
    latency_ms: float | None = None
    packet_loss: float | None = None
    throughput_mbps: float | None = None
    status: str = "unknown"

    def to_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        return payload
