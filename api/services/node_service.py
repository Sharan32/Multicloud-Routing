from __future__ import annotations

from typing import Any

from api.exceptions import NodeAlreadyExistsError, NodeNotFoundError
from api.repositories.node_repository import NodeRepository


class NodeService:
    """Service for managing configured monitoring nodes."""

    def __init__(self, repository: NodeRepository) -> None:
        self.repository = repository

    def list_nodes(self) -> list[dict[str, Any]]:
        return self.repository.list_nodes()

    def create_node(self, node_name: str, host: str, port: int) -> dict[str, Any]:
        existing_nodes = self.list_nodes()
        if any(node.get("node") == node_name for node in existing_nodes):
            raise NodeAlreadyExistsError(node_name)
        new_node = {"node": node_name, "host": host, "port": port}
        return self.repository.create_node(new_node)

    def delete_node(self, node_name: str) -> None:
        try:
            self.repository.delete_node(node_name)
        except KeyError as exc:
            raise NodeNotFoundError(node_name) from exc
