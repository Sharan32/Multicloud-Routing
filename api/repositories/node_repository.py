from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol


class NodeRepository(Protocol):
    """Abstraction for node persistence backends."""

    def list_nodes(self) -> list[dict[str, Any]]: ...

    def create_node(self, node: dict[str, Any]) -> dict[str, Any]: ...

    def delete_node(self, node_name: str) -> None: ...


class JsonNodeRepository:
    """JSON-backed repository for node persistence."""

    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def list_nodes(self) -> list[dict[str, Any]]:
        if not self.storage_path.exists():
            return []
        with self.storage_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict) and item.get("node")]
        return []

    def create_node(self, node: dict[str, Any]) -> dict[str, Any]:
        nodes = self.list_nodes()
        nodes.append(node)
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(nodes, handle, indent=2)
        return node

    def delete_node(self, node_name: str) -> None:
        nodes = self.list_nodes()
        remaining = [node for node in nodes if node.get("node") != node_name]
        if len(remaining) == len(nodes):
            raise KeyError(node_name)
        with self.storage_path.open("w", encoding="utf-8") as handle:
            json.dump(remaining, handle, indent=2)
