from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_metrics_service, get_routing_service
from api.logger import build_logger
from api.schemas.routing import ExecutionResponse, RoutingResponse
from api.services.metrics_service import MetricsService
from api.services.routing_service import RoutingService

router = APIRouter(tags=["routing"])
logger = build_logger("api.routing")


@router.get("/best-route", summary="Best route", description="Select the best route based on current metrics.", response_model=RoutingResponse)
def best_route(metrics_service: MetricsService = Depends(get_metrics_service), routing_service: RoutingService = Depends(get_routing_service)) -> RoutingResponse:
    """Return the currently selected route based on metrics."""

    logger.info("Best-route endpoint requested")
    metrics = metrics_service.get_all_metrics()
    decision = routing_service.decide_route(metrics)
    logger.info("Route selected node=%s score=%.2f", decision.selected_node, decision.score)
    return RoutingResponse(selected_node=decision.selected_node, algorithm=decision.algorithm, score=decision.score, reason=decision.reason)


@router.post("/execute-route", summary="Execute selected route", description="Request the best route, then apply it through the execution engine.", response_model=ExecutionResponse)
def execute_route(metrics_service: MetricsService = Depends(get_metrics_service), routing_service: RoutingService = Depends(get_routing_service)) -> ExecutionResponse:
    """Request the best route and execute it via the execution engine."""

    logger.info("Execute-route endpoint requested")
    metrics = metrics_service.get_all_metrics()
    decision = routing_service.decide_route(metrics)
    result = routing_service.execute_route(decision)
    logger.info("Route execution result=%s route=%s", result.reason, result.active_route)
    return ExecutionResponse(executed=result.executed, active_route=result.active_route, reason=result.reason, detail=result.detail)
