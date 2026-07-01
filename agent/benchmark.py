from __future__ import annotations

import subprocess
from datetime import datetime
from typing import Optional

from agent.logger import build_logger
from agent.models import NetworkMetrics
from agent.utils import is_command_available

logger = build_logger("agent.benchmark")


class BenchmarkRunner:
    """Run network throughput benchmarks for a target node."""

    def __init__(self, duration_seconds: int = 10) -> None:
        self.duration_seconds = duration_seconds

    def run(self, node: str) -> Optional[float]:
        if not is_command_available("iperf3"):
            logger.warning("iperf3 is not available; skipping benchmark")
            return None

        command = ["iperf3", "-c", node, "-t", str(self.duration_seconds), "-J"]
        logger.info("Running iperf3 benchmark for %s", node)
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=self.duration_seconds + 10)
            if completed.returncode != 0:
                logger.warning("iperf3 failed for %s: %s", node, completed.stderr.strip())
                return None
            payload = completed.stdout.strip()
            if not payload:
                return None
            import json

            summary = json.loads(payload)
            sender = summary.get("end", {}).get("sum_received", {}).get("bits_per_second")
            if sender is None:
                sender = summary.get("end", {}).get("sum_sent", {}).get("bits_per_second")
            if sender is None:
                return None
            return round(sender / (1024 * 1024), 2)
        except (subprocess.SubprocessError, json.JSONDecodeError, ValueError) as exc:
            logger.exception("Benchmark failed for %s: %s", node, exc)
            return None
