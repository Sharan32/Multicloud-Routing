from __future__ import annotations

from api.config import APIConfig
from executor.config import ExecutorConfig
from executor.executor import ExecutionResult, RouteExecutionEngine
from router.config import RoutingConfig
from router.engine import RoutingEngine
from router.models import RouteCandidate, RoutingDecision


class RoutingService:
    """Service for orchestrating routing decisions from metric snapshots."""

    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or APIConfig.from_env()
        self.router_config = RoutingConfig.from_env()
        self.engine = RoutingEngine(config=self.router_config)
        self.executor_config = ExecutorConfig.from_env()
        self.executor = RouteExecutionEngine(config=self.executor_config)

    def decide_route(self, metrics: list[dict[str, object]], previous_route: str | None = None, previous_score: float | None = None) -> RoutingDecision:
        candidates = []
        for item in metrics:
            raw_status = str(item.get("status") or "unknown")
            status = raw_status.lower()
            health_value = item.get("health")
            if health_value is None:
                health_value = 1.0 if status == "healthy" else 0.0
            uptime_value = item.get("uptime")
            if uptime_value is None:
                uptime_value = 100.0 if status == "healthy" else 0.0

            candidates.append(
                RouteCandidate(
                    node=str(item.get("node", "unknown")),
                    latency_ms=float(item.get("latency_ms") or 0.0),
                    packet_loss=float(item.get("packet_loss") or 0.0),
                    throughput_mbps=float(item.get("throughput_mbps") or 0.0),
                    health=float(health_value),
                    uptime=float(uptime_value),
                    status=raw_status,
                    raw_metrics=item,
                )
            )
        return self.engine.select_route(candidates, previous_route=previous_route, previous_score=previous_score)

    def execute_route(self, decision: RoutingDecision) -> ExecutionResult:
        return self.executor.execute(decision)
