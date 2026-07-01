from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from executor.config import ExecutorConfig
from executor.exceptions import ExecutorFailureError, InvalidRouteError
from executor.executor import RouteExecutionEngine, ExecutionResult
from executor.history import ExecutionHistoryStore
from executor.state import RouteStateStore
from router.models import RoutingDecision


class FailingRouteManager:
    def apply_route(self, route_name: str) -> None:
        raise RuntimeError("boom")


def make_decision(route_name: str) -> RoutingDecision:
    return RoutingDecision(selected_node=route_name, algorithm="weighted-score", score=80.0, reason="best available route", candidates=[])


def make_engine(tmp_path, cooldown_seconds: int = 0, valid_routes: set[str] | None = None):
    config = ExecutorConfig(
        history_path=str(tmp_path / "history.json"),
        state_path=str(tmp_path / "state.json"),
        cooldown_seconds=cooldown_seconds,
        valid_routes=valid_routes or {"aws-node", "local-node"},
    )
    state_store = RouteStateStore(config.state_path)
    history_store = ExecutionHistoryStore(config.history_path)
    return RouteExecutionEngine(config=config, state_store=state_store, history_store=history_store)


def test_successful_execution_updates_state_and_history(tmp_path):
    engine = make_engine(tmp_path)

    result = engine.execute(make_decision("aws-node"))

    assert isinstance(result, ExecutionResult)
    assert result.executed is True
    assert result.active_route == "aws-node"
    assert result.reason == "executed"
    assert engine.state_store.read().active_route == "aws-node"

    history = engine.history_store.read_all()
    assert len(history) == 1
    assert history[0].route == "aws-node"


def test_noop_when_already_on_best_route(tmp_path):
    engine = make_engine(tmp_path)
    engine.state_store.save(engine.state_store.default_state(active_route="aws-node"))

    result = engine.execute(make_decision("aws-node"))

    assert result.executed is False
    assert result.reason == "no-op"
    assert engine.state_store.read().active_route == "aws-node"


def test_cooldown_enforcement_blocks_switch(tmp_path):
    engine = make_engine(tmp_path, cooldown_seconds=60)
    engine.state_store.save(
        engine.state_store.default_state(active_route="local-node", last_switch_at=datetime.now(timezone.utc) - timedelta(seconds=30))
    )

    result = engine.execute(make_decision("aws-node"))

    assert result.executed is False
    assert result.reason == "cooldown"
    assert engine.state_store.read().active_route == "local-node"


def test_invalid_route_raises_error(tmp_path):
    engine = make_engine(tmp_path, valid_routes={"aws-node"})

    with pytest.raises(InvalidRouteError):
        engine.execute(make_decision("bad-route"))


def test_executor_failures_are_wrapped(tmp_path):
    config = ExecutorConfig(history_path=str(tmp_path / "history.json"), state_path=str(tmp_path / "state.json"), valid_routes={"aws-node"})
    state_store = RouteStateStore(config.state_path)
    history_store = ExecutionHistoryStore(config.history_path)
    engine = RouteExecutionEngine(config=config, state_store=state_store, history_store=history_store, route_manager=FailingRouteManager())

    with pytest.raises(ExecutorFailureError):
        engine.execute(make_decision("aws-node"))


def test_history_persistence(tmp_path):
    engine = make_engine(tmp_path)
    engine.execute(make_decision("aws-node"))

    with open(tmp_path / "history.json", encoding="utf-8") as handle:
        payload = json.load(handle)

    assert payload[0]["route"] == "aws-node"


def test_state_updates_persist_to_disk(tmp_path):
    engine = make_engine(tmp_path)
    engine.execute(make_decision("aws-node"))

    with open(tmp_path / "state.json", encoding="utf-8") as handle:
        payload = json.load(handle)

    assert payload["active_route"] == "aws-node"
    assert payload["last_switch_at"] is not None
