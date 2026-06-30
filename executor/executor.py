from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from executor.config import ExecutorConfig
from executor.exceptions import ExecutorFailureError, InvalidRouteError
from executor.history import ExecutionHistoryEntry, ExecutionHistoryStore
from executor.logger import build_logger
from executor.state import ExecutionState, RouteStateStore
from router.models import RoutingDecision


@dataclass(slots=True)
class ExecutionResult:
    """Result payload from attempting to execute a routing decision."""

    executed: bool
    active_route: str | None
    reason: str
    detail: str | None = None


class RouteExecutionEngine:
    """Consumes routing decisions and applies them safely."""

    def __init__(self, config: ExecutorConfig | None = None, state_store: RouteStateStore | None = None, history_store: ExecutionHistoryStore | None = None, route_manager: Any | None = None) -> None:
        self.config = config or ExecutorConfig.from_env()
        self.state_store = state_store or RouteStateStore(self.config.state_path)
        self.history_store = history_store or ExecutionHistoryStore(self.config.history_path)
        self.route_manager = route_manager or self._default_route_manager()
        self.logger = build_logger("executor.engine", log_level="info")

    def execute(self, decision: RoutingDecision) -> ExecutionResult:
        if decision.selected_node not in self.config.valid_routes and self.config.valid_routes:
            raise InvalidRouteError(f"Unsupported route: {decision.selected_node}")

        state = self.state_store.read()
        current_route = state.active_route

        if decision.selected_node == current_route:
            self._record_history(decision.selected_node, "no-op", executed=False)
            return ExecutionResult(executed=False, active_route=current_route, reason="no-op", detail="already active")

        if self._in_cooldown(state):
            self._record_history(decision.selected_node, "cooldown", executed=False)
            return ExecutionResult(executed=False, active_route=current_route, reason="cooldown", detail="cooldown active")

        try:
            self.route_manager.apply_route(decision.selected_node)
        except Exception as exc:  # pragma: no cover - defensive branch
            self.logger.exception("Route execution failed for %s", decision.selected_node)
            raise ExecutorFailureError(str(exc)) from exc

        state.active_route = decision.selected_node
        state.last_switch_at = datetime.now(timezone.utc)
        self.state_store.save(state)
        self._record_history(decision.selected_node, "executed", executed=True)
        return ExecutionResult(executed=True, active_route=decision.selected_node, reason="executed", detail="route applied")

    def _in_cooldown(self, state: ExecutionState) -> bool:
        if self.config.cooldown_seconds <= 0:
            return False
        if state.last_switch_at is None:
            return False
        return datetime.now(timezone.utc) - state.last_switch_at < timedelta(seconds=self.config.cooldown_seconds)

    def _record_history(self, route: str, reason: str, executed: bool) -> None:
        entry = ExecutionHistoryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            route=route,
            reason=reason,
            executed=executed,
        )
        self.history_store.append(entry)

    def _default_route_manager(self) -> Any:
        from executor.linux_routes import LinuxRouteManager

        return LinuxRouteManager()
