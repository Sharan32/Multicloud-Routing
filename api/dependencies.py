from __future__ import annotations

from fastapi import Depends, Request

from api.config import APIConfig
from api.logger import build_logger
from api.repositories.metrics_repository import MetricsRepository
from api.repositories.node_repository import JsonNodeRepository
from api.services.benchmark_service import BenchmarkService
from api.services.metrics_service import MetricsService
from api.services.node_service import NodeService
from api.services.routing_service import RoutingService


def get_api_config(request: Request) -> APIConfig:
    return request.app.state.api_config


def get_logger(request: Request) -> object:
    config = get_api_config(request)
    return build_logger("api", log_level=config.log_level)


def get_metrics_repository(request: Request) -> MetricsRepository:
    config = get_api_config(request)
    return MetricsRepository(config.storage_path)


def get_metrics_service(repository: MetricsRepository = Depends(get_metrics_repository)) -> MetricsService:
    return MetricsService(repository)


def get_node_repository(request: Request) -> JsonNodeRepository:
    config = get_api_config(request)
    return JsonNodeRepository(config.nodes_storage_path)


def get_node_service(repository: JsonNodeRepository = Depends(get_node_repository)) -> NodeService:
    return NodeService(repository)


def get_benchmark_service(request: Request) -> BenchmarkService:
    config = get_api_config(request)
    return BenchmarkService(timeout_seconds=config.benchmark_timeout_seconds)


def get_routing_service(request: Request) -> RoutingService:
    config = get_api_config(request)
    return RoutingService(config=config)
