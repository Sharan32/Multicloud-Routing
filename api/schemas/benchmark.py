from __future__ import annotations

from pydantic import BaseModel, Field


class BenchmarkRequest(BaseModel):
    """Schema for triggering a benchmark request."""

    node: str = Field(min_length=1)


class BenchmarkResponse(BaseModel):
    """Response schema for a benchmark execution."""

    node: str
    throughput_mbps: float | None = None
    status: str
