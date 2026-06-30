from datetime import datetime

from agent.config import AgentConfig
from agent.models import NetworkMetrics


def test_agent_config_reads_env_values(monkeypatch):
    monkeypatch.setenv("AGENT_PING_INTERVAL_SECONDS", "45")
    monkeypatch.setenv("AGENT_TARGET_NODES", "node-a,node-b")

    config = AgentConfig.from_env()

    assert config.ping_interval_seconds == 45
    assert config.target_nodes == ["node-a", "node-b"]


def test_network_metrics_payload_serializes_timestamp():
    metrics = NetworkMetrics(
        timestamp=datetime(2026, 6, 30, 12, 0, 0),
        node="aws-node",
        latency_ms=18.2,
        packet_loss=0.0,
        throughput_mbps=941.0,
        status="healthy",
    )

    payload = metrics.to_payload()

    assert payload["node"] == "aws-node"
    assert payload["status"] == "healthy"
    assert payload["timestamp"] == "2026-06-30T12:00:00"
