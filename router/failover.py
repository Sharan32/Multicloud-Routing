from __future__ import annotations

from datetime import datetime
from typing import Any

from router.config import RoutingConfig
from router.exceptions import NoHealthyNodeError
from router.models import FailoverEvent, RouteCandidate


class FailoverManager:
    """Selects a backup node when the currently preferred route becomes unhealthy."""

    def __init__(self, config: RoutingConfig) -> None:
        self.config = config

    def should_failover(self, candidate: RouteCandidate) -> bool:
        if candidate.status != "healthy":
            return True
        if candidate.latency_ms is not None and candidate.latency_ms > self.config.latency_threshold_ms:
            return True
        if candidate.packet_loss is not None and candidate.packet_loss > self.config.packet_loss_threshold:
            return True
        if candidate.throughput_mbps is not None and candidate.throughput_mbps < self.config.minimum_throughput_mbps:
            return True
        if candidate.health is not None and candidate.health < self.config.health_score_threshold:
            return True
        return False

    def select_backup(self, candidates: list[RouteCandidate]) -> RouteCandidate:
        healthy_candidates = [candidate for candidate in candidates if not self.should_failover(candidate)]
        if not healthy_candidates:
            raise NoHealthyNodeError()
        return sorted(healthy_candidates, key=lambda item: (item.latency_ms or 9999, item.packet_loss or 100),)[0]

    def build_event(self, from_node: str, to_node: str, reason: str) -> FailoverEvent:
        return FailoverEvent(timestamp=datetime.utcnow().isoformat(), from_node=from_node, to_node=to_node, reason=reason)
