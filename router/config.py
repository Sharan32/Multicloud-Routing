from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class RoutingConfig:
    """Configuration for routing decisions and failover behavior."""

    latency_weight: float = 0.4
    packet_loss_weight: float = 0.3
    throughput_weight: float = 0.2
    health_weight: float = 0.1
    uptime_weight: float = 0.0
    latency_threshold_ms: float = 200.0
    packet_loss_threshold: float = 5.0
    minimum_throughput_mbps: float = 10.0
    health_score_threshold: float = 0.6
    failover_cooldown_seconds: int = 60
    benchmark_timeout_seconds: int = 20
    algorithm: str = "weighted-score"
    default_policy: str = "weighted-score"
    history_path: str = "./data/router_history.json"
    failover_path: str = "./data/failover_history.json"

    @classmethod
    def from_env(cls) -> "RoutingConfig":
        return cls(
            latency_weight=float(os.getenv("ROUTER_LATENCY_WEIGHT", "0.4")),
            packet_loss_weight=float(os.getenv("ROUTER_PACKET_LOSS_WEIGHT", "0.3")),
            throughput_weight=float(os.getenv("ROUTER_THROUGHPUT_WEIGHT", "0.2")),
            health_weight=float(os.getenv("ROUTER_HEALTH_WEIGHT", "0.1")),
            uptime_weight=float(os.getenv("ROUTER_UPTIME_WEIGHT", "0.0")),
            latency_threshold_ms=float(os.getenv("ROUTER_LATENCY_THRESHOLD_MS", "200")),
            packet_loss_threshold=float(os.getenv("ROUTER_PACKET_LOSS_THRESHOLD", "5")),
            minimum_throughput_mbps=float(os.getenv("ROUTER_MINIMUM_THROUGHPUT_MBPS", "10")),
            health_score_threshold=float(os.getenv("ROUTER_HEALTH_SCORE_THRESHOLD", "0.6")),
            failover_cooldown_seconds=int(os.getenv("ROUTER_FAILOVER_COOLDOWN_SECONDS", "60")),
            benchmark_timeout_seconds=int(os.getenv("ROUTER_BENCHMARK_TIMEOUT_SECONDS", "20")),
            algorithm=os.getenv("ROUTER_ALGORITHM", "weighted-score"),
            default_policy=os.getenv("ROUTER_DEFAULT_POLICY", "weighted-score"),
            history_path=os.getenv("ROUTER_HISTORY_PATH", "./data/router_history.json"),
            failover_path=os.getenv("ROUTER_FAILOVER_PATH", "./data/failover_history.json"),
        )
