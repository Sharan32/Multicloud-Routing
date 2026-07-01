from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class AgentConfig:
    """Configuration for the network monitoring agent."""

    ping_interval_seconds: int = 30
    ping_timeout_seconds: float = 2.0
    ping_retry_count: int = 2
    target_nodes: List[str] = field(default_factory=lambda: ["aws-node"])
    iperf3_duration_seconds: int = 10
    output_file: str = "./data/metrics.json"

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls(
            ping_interval_seconds=int(os.getenv("AGENT_PING_INTERVAL_SECONDS", "30")),
            ping_timeout_seconds=float(os.getenv("AGENT_PING_TIMEOUT_SECONDS", "2.0")),
            ping_retry_count=int(os.getenv("AGENT_PING_RETRY_COUNT", "2")),
            target_nodes=[node.strip() for node in os.getenv("AGENT_TARGET_NODES", "aws-node").split(",") if node.strip()],
            iperf3_duration_seconds=int(os.getenv("AGENT_IPERF3_DURATION_SECONDS", "10")),
            output_file=os.getenv("AGENT_OUTPUT_FILE", "./data/metrics.json"),
        )
