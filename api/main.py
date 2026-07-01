from __future__ import annotations

import time
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from api.config import APIConfig
from api.exceptions import APIError
from api.logger import build_logger
from api.routers.benchmark import router as benchmark_router
from api.routers.health import router as health_router
from api.routers.metrics import router as metrics_router
from api.routers.nodes import router as nodes_router
from api.routers.routing import router as routing_router


def create_app(config: APIConfig | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    app_config = config or APIConfig.from_env()
    logger = build_logger("api.main", log_level=app_config.log_level)
    app = FastAPI(title="Multicloud Routing API", version="1.0.0", debug=app_config.debug)
    app.state.api_config = app_config

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(nodes_router)
    app.include_router(benchmark_router)
    app.include_router(routing_router)

    @app.exception_handler(APIError)
    async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message, "status": exc.status_code})

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        normalized_errors = []
        for error in exc.errors():
            normalized_error = {
                "loc": error.get("loc", []),
                "msg": error.get("msg", "Validation failed"),
                "type": error.get("type", "validation_error"),
            }
            normalized_errors.append(normalized_error)
        return JSONResponse(status_code=422, content={"error": "Validation failed", "status": 422, "details": normalized_errors})

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception for %s %s", request.method, request.url.path)
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error", "status": 500})

    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable[[Request], object]) -> object:
        start_time = time.perf_counter()
        logger.info("Incoming request method=%s path=%s", request.method, request.url.path)
        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info("Completed request method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, duration_ms)
            return response
        except Exception as exc:  # pragma: no cover - defensive logging
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception("Failed request method=%s path=%s duration_ms=%.2f error=%s", request.method, request.url.path, duration_ms, exc)
            raise

    return app


app = create_app()
