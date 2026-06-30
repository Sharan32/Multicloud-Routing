import os

import pytest

from router.config import RoutingConfig
from router.engine import RoutingEngine
from router.exceptions import NoHealthyNodeError, NoMetricsAvailableError
from router.history import HistoryStore
from router.models import RouteCandidate


def test_select_route_prefers_low_latency_candidate(tmp_path):
    config = RoutingConfig(history_path=str(tmp_path / "history.json"))
    engine = RoutingEngine(config=config, history_store=HistoryStore(str(tmp_path / "history.json")))

    candidates = [
        RouteCandidate(node="aws-node", latency_ms=80.0, packet_loss=0.0, throughput_mbps=100.0, health=1.0, uptime=100.0, status="healthy"),
        RouteCandidate(node="local-node", latency_ms=20.0, packet_loss=0.0, throughput_mbps=120.0, health=1.0, uptime=100.0, status="healthy"),
    ]

    decision = engine.select_route(candidates)

    assert decision.selected_node == "local-node"
    assert decision.score > 80


def test_select_route_raises_when_no_healthy_nodes():
    config = RoutingConfig(latency_threshold_ms=50.0, packet_loss_threshold=1.0, minimum_throughput_mbps=10.0)
    engine = RoutingEngine(config=config)

    candidates = [
        RouteCandidate(node="aws-node", latency_ms=200.0, packet_loss=10.0, throughput_mbps=5.0, health=0.2, uptime=50.0, status="degraded"),
    ]

    with pytest.raises(NoHealthyNodeError):
        engine.select_route(candidates)


def test_select_route_raises_when_no_metrics():
    engine = RoutingEngine(config=RoutingConfig())

    with pytest.raises(NoMetricsAvailableError):
        engine.select_route([])


def test_history_is_recorded(tmp_path):
    history_path = tmp_path / "history.json"
    config = RoutingConfig(history_path=str(history_path))
    engine = RoutingEngine(config=config, history_store=HistoryStore(str(history_path)))

    engine.select_route([
        RouteCandidate(node="aws-node", latency_ms=20.0, packet_loss=0.0, throughput_mbps=100.0, health=1.0, uptime=100.0, status="healthy"),
    ], previous_route="local-node", previous_score=60.0)

    history = HistoryStore(str(history_path)).read_all()
    assert len(history) == 1
    assert history[0].old_route == "local-node"
    assert history[0].new_route == "aws-node"
