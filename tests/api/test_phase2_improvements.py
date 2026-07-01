import json

import pytest
from fastapi.testclient import TestClient

from api.config import APIConfig
from api.main import create_app
from api.repositories.metrics_repository import MetricsRepository
from api.repositories.node_repository import JsonNodeRepository
from api.services.node_service import NodeService
from api.exceptions import NodeAlreadyExistsError, NodeNotFoundError


def test_metrics_repository_handles_corrupt_json(tmp_path):
    storage_path = tmp_path / "metrics.json"
    storage_path.write_text("{not valid json", encoding="utf-8")

    repository = MetricsRepository(str(storage_path))

    assert repository.read_metrics() == []
    assert repository.get_latest_metrics() is None


def test_node_service_raises_domain_error_on_duplicate(tmp_path):
    storage_path = tmp_path / "nodes.json"
    repository = JsonNodeRepository(str(storage_path))
    service = NodeService(repository)

    service.create_node("aws-node", "10.0.0.10", 22)

    with pytest.raises(NodeAlreadyExistsError):
        service.create_node("aws-node", "10.0.0.10", 22)


def test_node_service_raises_domain_error_when_missing(tmp_path):
    storage_path = tmp_path / "nodes.json"
    repository = JsonNodeRepository(str(storage_path))
    service = NodeService(repository)

    with pytest.raises(NodeNotFoundError):
        service.delete_node("missing-node")


def test_api_returns_not_found_when_metrics_storage_is_corrupt(tmp_path):
    storage_path = tmp_path / "metrics.json"
    storage_path.write_text("{not valid json", encoding="utf-8")
    app = create_app(APIConfig(storage_path=str(storage_path)))
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 404
    assert response.json()["error"] == "No metrics available"
