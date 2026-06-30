from __future__ import annotations

from pydantic import BaseModel, Field


class MetricsResponse(BaseModel):
    """Response schema for a metrics payload."""

    timestamp: str
    node: str = Field(min_length=1)
    latency_ms: float | None = None
    packet_loss: float | None = None
    throughput_mbps: float | None = None
    status: str = Field(min_length=1)
