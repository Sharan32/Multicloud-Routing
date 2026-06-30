from __future__ import annotations

from fastapi import APIRouter, Depends, status

from api.dependencies import get_node_service
from api.logger import build_logger
from api.schemas.node import NodeCreateRequest, NodeResponse
from api.services.node_service import NodeService

router = APIRouter(tags=["nodes"])
logger = build_logger("api.nodes")


@router.get("/nodes", summary="List nodes", description="Return all configured monitoring nodes.", response_model=list[NodeResponse])
def list_nodes(service: NodeService = Depends(get_node_service)) -> list[NodeResponse]:
    """Return all configured monitoring nodes."""

    logger.info("Node listing requested")
    return [NodeResponse(**node) for node in service.list_nodes()]


@router.post("/nodes", status_code=status.HTTP_201_CREATED, summary="Register node", description="Register a new monitoring node.", response_model=NodeResponse)
def create_node(payload: NodeCreateRequest, service: NodeService = Depends(get_node_service)) -> NodeResponse:
    """Register a new monitoring node."""

    logger.info("Node creation requested for %s", payload.name)
    node = service.create_node(payload.name, payload.host, payload.port)
    logger.info("Node registration completed name=%s", payload.name)
    return NodeResponse(**node)


@router.delete("/nodes/{node_name}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete node", description="Remove a node from the configured list.")
def delete_node(node_name: str, service: NodeService = Depends(get_node_service)) -> None:
    """Remove a node from the configured list."""

    logger.info("Node removal requested for %s", node_name)
    service.delete_node(node_name)
    logger.info("Node removal completed name=%s", node_name)
