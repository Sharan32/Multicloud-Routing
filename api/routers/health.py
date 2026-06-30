from __future__ import annotations

from fastapi import APIRouter, Depends

from api.config import APIConfig
from api.dependencies import get_api_config
from api.logger import build_logger

router = APIRouter(tags=["health"])
logger = build_logger("api.health")


@router.get("/health", summary="API health", description="Returns basic API health information.", response_model=dict[str, str])
def health(config: APIConfig = Depends(get_api_config)) -> dict[str, str]:
    """Return API health status."""

    logger.info("Health check requested")
    return {"status": "healthy", "service": "multicloud-api", "version": "1.0.0"}
