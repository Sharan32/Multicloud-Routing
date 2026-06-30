from __future__ import annotations

from typing import Protocol

from router.models import NodeScore, RouteCandidate


class RoutingPolicy(Protocol):
    """Protocol for routing algorithms."""

    name: str

    def score(self, candidate: RouteCandidate) -> NodeScore: ...


class WeightedScorePolicy:
    """Weighted scoring policy with configurable component weights."""

    name = "weighted-score"

    def __init__(self, config) -> None:
        self.config = config

    def score(self, candidate: RouteCandidate) -> NodeScore:
        latency_score = self._normalize_latency(candidate.latency_ms)
        packet_loss_score = self._normalize_packet_loss(candidate.packet_loss)
        throughput_score = self._normalize_throughput(candidate.throughput_mbps)
        health_score = self._normalize_health(candidate.health)
        uptime_score = self._normalize_uptime(candidate.uptime)

        total = (
            (latency_score * self.config.latency_weight)
            + (packet_loss_score * self.config.packet_loss_weight)
            + (throughput_score * self.config.throughput_weight)
            + (health_score * self.config.health_weight)
            + (uptime_score * self.config.uptime_weight)
        )

        return NodeScore(
            node=candidate.node,
            score=round(total * 100, 2),
            latency_score=round(latency_score * 100, 2),
            packet_loss_score=round(packet_loss_score * 100, 2),
            throughput_score=round(throughput_score * 100, 2),
            health_score=round(health_score * 100, 2),
            uptime_score=round(uptime_score * 100, 2),
            reason=self._explain(candidate, total),
        )

    def _normalize_latency(self, latency_ms: float | None) -> float:
        if latency_ms is None:
            return 0.0
        if latency_ms <= 0:
            return 1.0
        max_latency = max(self.config.latency_threshold_ms, 1.0)
        return max(0.0, min(1.0, 1 - (latency_ms / max_latency)))

    def _normalize_packet_loss(self, packet_loss: float | None) -> float:
        if packet_loss is None:
            return 0.0
        return max(0.0, min(1.0, 1 - (packet_loss / 100.0)))

    def _normalize_throughput(self, throughput_mbps: float | None) -> float:
        if throughput_mbps is None:
            return 0.0
        minimum = max(self.config.minimum_throughput_mbps, 1.0)
        return max(0.0, min(1.0, throughput_mbps / (minimum * 4)))

    def _normalize_health(self, health: float | None) -> float:
        if health is None:
            return 0.0
        return max(0.0, min(1.0, health))

    def _normalize_uptime(self, uptime: float | None) -> float:
        if uptime is None:
            return 0.0
        return max(0.0, min(1.0, uptime / 100.0))

    def _explain(self, candidate: RouteCandidate, total: float) -> str:
        return (
            f"latency={candidate.latency_ms}ms packet_loss={candidate.packet_loss}% "
            f"throughput={candidate.throughput_mbps}mbps health={candidate.health}"
        )
