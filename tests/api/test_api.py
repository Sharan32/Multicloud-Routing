from fastapi.testclient import TestClient

from api.config import APIConfig
from api.main import create_app


def test_health_endpoint(tmp_path):
    config = APIConfig(storage_path=str(tmp_path / "metrics.json"), nodes_storage_path=str(tmp_path / "nodes.json"))
    app = create_app(config)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_metrics_endpoint_returns_404_when_empty(tmp_path):
    config = APIConfig(storage_path=str(tmp_path / "metrics.json"), nodes_storage_path=str(tmp_path / "nodes.json"))
    app = create_app(config)
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 404
    assert response.json()["error"] == "No metrics available"


def test_node_creation_and_listing(tmp_path):
    config = APIConfig(storage_path=str(tmp_path / "metrics.json"), nodes_storage_path=str(tmp_path / "nodes.json"))
    app = create_app(config)
    client = TestClient(app)

    create_response = client.post("/nodes", json={"name": "aws-node", "host": "10.0.0.10", "port": 22})
    list_response = client.get("/nodes")

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert list_response.json()[0]["node"] == "aws-node"


def test_validation_failure_for_invalid_node_name(tmp_path):
    config = APIConfig(storage_path=str(tmp_path / "metrics.json"), nodes_storage_path=str(tmp_path / "nodes.json"))
    app = create_app(config)
    client = TestClient(app)

    response = client.post("/nodes", json={"name": "bad name", "host": "10.0.0.10", "port": 22})

    assert response.status_code == 422
