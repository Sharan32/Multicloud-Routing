from __future__ import annotations

import time

from agent.collector import MetricsCollector
from agent.config import AgentConfig
from agent.logger import build_logger

logger = build_logger("agent.main")


def run_agent(config: AgentConfig | None = None) -> None:
    """Continuously collect metrics for configured nodes."""

    agent_config = config or AgentConfig.from_env()
    collector = MetricsCollector(agent_config)
    logger.info("Starting monitoring agent with config %s", agent_config)

    try:
        while True:
            collector.collect_all()
            time.sleep(agent_config.ping_interval_seconds)
    except KeyboardInterrupt:
        logger.info("Monitoring agent stopped")


if __name__ == "__main__":
    run_agent()
