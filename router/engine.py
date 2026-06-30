from __future__ import annotations

from datetime import datetime
from typing import Any

from router.algorithms import RoutingAlgorithm, ScoreCalculator
from router.config import RoutingConfig
from router.exceptions import NoHealthyNodeError, NoMetricsAvailableError, RoutingFailureError
from router.failover import FailoverManager
from router.history import HistoryStore
from router.logger import build_logger
from router.models import RouteCandidate, RoutingDecision, RouteHistoryEntry


class RoutingEngine:
    """Central routing engine that evaluates candidate nodes and selects the best route."""

    def __init__(self, config: RoutingConfig | None = None, history_store: HistoryStore | None = None) -> None:
        self.config = config or RoutingConfig.from_env()
        self.history_store = history_store or HistoryStore(self.config.history_path)
        self.logger = build_logger("router.engine", log_level=getattr(self.config, "log_level", "info"))
        self.algorithm_factory = RoutingAlgorithm(self.config)
        self.failover_manager = FailoverManager(self.config)

    def select_route(self, candidates: list[RouteCandidate], previous_route: str | None = None, previous_score: float | None = None) -> RoutingDecision:
        if not candidates:
            raise NoMetricsAvailableError()

        self.logger.info("Routing started candidates=%s", [candidate.node for candidate in candidates])
        policy = self.algorithm_factory.create_policy(self.config.algorithm)
        calculator = ScoreCalculator(policy)
        scored_candidates = calculator.score_candidates(candidates)
        self.logger.info("Node scores: %s", [(score.node, score.score) for score in scored_candidates])

        best_candidate = max(scored_candidates, key=lambda score: score.score)
        best_route_candidate = self._candidate_from_score(best_candidate, candidates)
        if self.failover_manager.should_failover(best_route_candidate):
            backup_candidates = [candidate for candidate in candidates if not self.failover_manager.should_failover(candidate)]
            if backup_candidates:
                backup = max(
                    [
                        score for score in scored_candidates if any(candidate.node == score.node for candidate in backup_candidates)
                    ],
                    key=lambda score: score.score,
                )
                best_candidate = backup
            else:
                self.logger.warning("No healthy candidate met score threshold")
                raise NoHealthyNodeError()

        decision = RoutingDecision(
            selected_node=best_candidate.node,
            algorithm=policy.name,
            score=best_candidate.score,
            reason=best_candidate.reason,
            candidates=scored_candidates,
        )

        self._record_history(previous_route, decision, previous_score)
        return decision

    def _record_history(self, previous_route: str | None, decision: RoutingDecision, previous_score: float | None) -> None:
        history_entry = RouteHistoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            old_route=previous_route,
            new_route=decision.selected_node,
            reason=decision.reason,
            old_score=previous_score,
            new_score=decision.score,
        )
        self.history_store.append(history_entry)

    def _candidate_from_score(self, score: Any, candidates: list[RouteCandidate]) -> RouteCandidate:
        for candidate in candidates:
            if candidate.node == score.node:
                return candidate
        raise RoutingFailureError()
