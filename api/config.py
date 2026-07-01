from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class APIConfig:
    """Configuration for the FastAPI control plane."""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    storage_path: str = "./data/metrics.json"
    nodes_storage_path: str = "./data/nodes.json"
    log_level: str = "info"
    benchmark_timeout_seconds: int = 20
    default_node_list: list[str] = field(default_factory=lambda: ["aws-node"])

    @classmethod
    def from_env(cls) -> "APIConfig":
        return cls(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            debug=os.getenv("API_DEBUG", "false").lower() == "true",
            cors_origins=[value.strip() for value in os.getenv("API_CORS_ORIGINS", "*").split(",") if value.strip()],
            storage_path=os.getenv("API_STORAGE_PATH", "./data/metrics.json"),
            nodes_storage_path=os.getenv("API_NODES_STORAGE_PATH", "./data/nodes.json"),
            log_level=os.getenv("API_LOG_LEVEL", "info"),
            benchmark_timeout_seconds=int(os.getenv("API_BENCHMARK_TIMEOUT_SECONDS", "20")),
            default_node_list=[value.strip() for value in os.getenv("API_DEFAULT_NODE_LIST", "aws-node").split(",") if value.strip()],
        )
