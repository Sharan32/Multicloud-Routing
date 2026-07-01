from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RouteCandidate:
    """A candidate node with its raw metric snapshot."""

    node: str
    latency_ms: float | None = None
    packet_loss: float | None = None
    throughput_mbps: float | None = None
    health: float | None = None
    uptime: float | None = None
    status: str = "unknown"
    raw_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NodeScore:
    """The computed score for a node under a given policy."""

    node: str
    score: float
    latency_score: float
    packet_loss_score: float
    throughput_score: float
    health_score: float
    uptime_score: float
    reason: str


@dataclass(slots=True)
class RoutingDecision:
    """The final selected route and explanation."""

    selected_node: str
    algorithm: str
    score: float
    reason: str
    candidates: list[NodeScore] = field(default_factory=list)


@dataclass(slots=True)
class RouteHistoryEntry:
    """A persisted history record of routing changes."""

    timestamp: str
    old_route: str | None
    new_route: str
    reason: str
    old_score: float | None
    new_score: float


@dataclass(slots=True)
class FailoverEvent:
    """Represents a failover action taken by the routing engine."""

    timestamp: str
    from_node: str
    to_node: str
    reason: str
