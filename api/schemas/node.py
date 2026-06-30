from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class NodeCreateRequest(BaseModel):
    """Schema for registering a monitoring node."""

    name: str = Field(min_length=1, max_length=64)
    host: str = Field(min_length=1, max_length=253)
    port: int = Field(ge=1, le=65535)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("node names may only contain letters, numbers, hyphens, or underscores")
        return value

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str) -> str:
        if value.count(".") == 0:
            raise ValueError("host must be a hostname or IP address")
        return value


class NodeResponse(BaseModel):
    """Response schema for a registered node."""

    node: str
    host: str
    port: int
