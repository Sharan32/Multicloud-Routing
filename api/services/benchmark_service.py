from __future__ import annotations

from agent.benchmark import BenchmarkRunner


class BenchmarkService:
    """Service for running benchmark jobs through the agent benchmark runner."""

    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds
        self.runner = BenchmarkRunner(duration_seconds=timeout_seconds)

    def run_benchmark(self, node: str) -> dict[str, object]:
        throughput = self.runner.run(node)
        return {
            "node": node,
            "throughput_mbps": throughput,
            "status": "completed" if throughput is not None else "failed",
        }
