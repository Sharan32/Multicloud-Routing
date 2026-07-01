from __future__ import annotations

from pydantic import BaseModel


class RoutingResponse(BaseModel):
    """Response schema for route decisions."""

    selected_node: str
    algorithm: str
    score: float
    reason: str


class ExecutionResponse(BaseModel):
    """Response schema for route execution results."""

    executed: bool
    active_route: str | None
    reason: str
    detail: str | None = None
