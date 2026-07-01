from __future__ import annotations

import subprocess
from datetime import datetime
from typing import Optional

from agent.benchmark import BenchmarkRunner
from agent.logger import build_logger
from agent.models import NetworkMetrics
from agent.utils import write_metrics

logger = build_logger("agent.collector")


class MetricsCollector:
    """Collect latency, packet loss, and throughput information for target nodes."""

    def __init__(self, config) -> None:
        self.config = config
        self.benchmark_runner = BenchmarkRunner(duration_seconds=config.iperf3_duration_seconds)

    def collect_once(self, node: str) -> NetworkMetrics:
        latency_ms = self._ping_node(node)
        packet_loss = self._estimate_packet_loss(node)
        throughput_mbps = self.benchmark_runner.run(node)

        status = "healthy"
        if packet_loss is not None and packet_loss > 0:
            status = "degraded"
        if latency_ms is not None and latency_ms > 200:
            status = "degraded"
        if throughput_mbps is None:
            status = "unreachable"

        metrics = NetworkMetrics(
            timestamp=datetime.utcnow(),
            node=node,
            latency_ms=latency_ms,
            packet_loss=packet_loss,
            throughput_mbps=throughput_mbps,
            status=status,
        )
        self.persist(metrics)
        return metrics

    def collect_all(self) -> list[NetworkMetrics]:
        return [self.collect_once(node) for node in self.config.target_nodes]

    def persist(self, metrics: NetworkMetrics) -> None:
        write_metrics(metrics, self.config.output_file)
        logger.info("Persisted metrics for %s", metrics.node)

    def _ping_node(self, node: str) -> Optional[float]:
        command = ["ping", "-c", "3", "-W", str(self.config.ping_timeout_seconds), node]
        logger.info("Pinging %s", node)
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=self.config.ping_timeout_seconds + 5)
            if completed.returncode != 0:
                logger.warning("Ping failed for %s: %s", node, completed.stderr.strip() or completed.stdout.strip())
                return None
            output = completed.stdout
            if "avg" not in output:
                return None
            average = output.split("/", 2)[-1].split("/", 1)[0]
            return round(float(average), 2)
        except (subprocess.SubprocessError, ValueError) as exc:
            logger.exception("Ping failed for %s: %s", node, exc)
            return None

    def _estimate_packet_loss(self, node: str) -> Optional[float]:
        command = ["ping", "-c", "3", "-W", str(self.config.ping_timeout_seconds), node]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=self.config.ping_timeout_seconds + 5)
            if completed.returncode != 0:
                return 100.0
            output = completed.stdout
            if "received" not in output or "transmitted" not in output:
                return None
            received = int(output.split("received,", 1)[1].split("packet", 1)[0].strip())
            transmitted = int(output.split("transmitted,", 1)[0].split()[-1])
            return round(((transmitted - received) / transmitted) * 100, 2)
        except (subprocess.SubprocessError, ValueError) as exc:
            logger.exception("Packet loss check failed for %s: %s", node, exc)
            return None
