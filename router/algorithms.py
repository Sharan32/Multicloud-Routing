from __future__ import annotations

from typing import Callable

from router.models import NodeScore, RouteCandidate
from router.policies import RoutingPolicy, WeightedScorePolicy


class RoutingAlgorithm:
    """Factory for creating routing policies by name."""

    def __init__(self, config) -> None:
        self.config = config

    def create_policy(self, name: str | None = None) -> RoutingPolicy:
        policy_name = name or self.config.algorithm or self.config.default_policy
        if policy_name == "weighted-score":
            return WeightedScorePolicy(self.config)
        raise ValueError(f"Unsupported routing algorithm: {policy_name}")


class ScoreCalculator:
    """Applies a policy to a list of route candidates."""

    def __init__(self, policy: RoutingPolicy) -> None:
        self.policy = policy

    def score_candidates(self, candidates: list[RouteCandidate]) -> list[NodeScore]:
        return [self.policy.score(candidate) for candidate in candidates]
