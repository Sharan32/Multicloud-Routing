from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_metrics_service
from api.logger import build_logger
from api.schemas.metrics import MetricsResponse
from api.services.metrics_service import MetricsService

router = APIRouter(tags=["metrics"])
logger = build_logger("api.metrics")


@router.get("/metrics", summary="Latest metrics", description="Returns all collected metrics from the monitoring agent.", response_model=list[MetricsResponse])
def read_metrics(service: MetricsService = Depends(get_metrics_service)) -> list[MetricsResponse]:
    """Return all collected metrics."""

    logger.info("Metrics endpoint requested")
    metrics = service.get_all_metrics()
    logger.info("Metrics retrieval completed count=%s", len(metrics))
    return [MetricsResponse(**item) for item in metrics]
