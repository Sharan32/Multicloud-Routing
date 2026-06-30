from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_benchmark_service
from api.logger import build_logger
from api.schemas.benchmark import BenchmarkRequest, BenchmarkResponse
from api.services.benchmark_service import BenchmarkService

router = APIRouter(tags=["benchmark"])
logger = build_logger("api.benchmark")


@router.post("/benchmark", summary="Run benchmark", description="Trigger a throughput benchmark for a target node.", response_model=BenchmarkResponse)
def run_benchmark(payload: BenchmarkRequest, service: BenchmarkService = Depends(get_benchmark_service)) -> BenchmarkResponse:
    """Trigger a benchmark for a target node."""

    logger.info("Benchmark requested for %s", payload.node)
    result = service.run_benchmark(payload.node)
    logger.info("Benchmark completed for %s status=%s", payload.node, result["status"])
    return BenchmarkResponse(**result)
