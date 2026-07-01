from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class ExecutorConfig:
    """Configuration for the route execution engine."""

    history_path: str = "./data/execution_history.json"
    state_path: str = "./data/execution_state.json"
    cooldown_seconds: int = 60
    valid_routes: set[str] = field(default_factory=set)
    simulation_mode: bool = True

    @classmethod
    def from_env(cls) -> "ExecutorConfig":
        valid_routes = os.getenv("EXECUTOR_VALID_ROUTES", "")
        return cls(
            history_path=os.getenv("EXECUTOR_HISTORY_PATH", "./data/execution_history.json"),
            state_path=os.getenv("EXECUTOR_STATE_PATH", "./data/execution_state.json"),
            cooldown_seconds=int(os.getenv("EXECUTOR_COOLDOWN_SECONDS", "60")),
            valid_routes={route.strip() for route in valid_routes.split(",") if route.strip()},
            simulation_mode=os.getenv("EXECUTOR_SIMULATION_MODE", "true").lower() == "true",
        )
