from fastapi.testclient import TestClient

from api.config import APIConfig
from api.main import create_app


def test_best_route_uses_routing_engine(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    nodes_path = tmp_path / "nodes.json"
    metrics_path.write_text(
        '[{"timestamp":"2026-01-01T00:00:00","node":"aws-node","latency_ms":80,"packet_loss":0,"throughput_mbps":100,"status":"healthy"}]',
        encoding="utf-8",
    )

    app = create_app(APIConfig(storage_path=str(metrics_path), nodes_storage_path=str(nodes_path)))
    client = TestClient(app)

    response = client.get("/best-route")

    assert response.status_code == 200
    assert response.json()["selected_node"] == "aws-node"


def test_execute_route_endpoint_returns_execution_result(tmp_path, monkeypatch):
    metrics_path = tmp_path / "metrics.json"
    nodes_path = tmp_path / "nodes.json"
    state_path = tmp_path / "execution_state.json"
    history_path = tmp_path / "execution_history.json"
    metrics_path.write_text(
        '[{"timestamp":"2026-01-01T00:00:00","node":"aws-node","latency_ms":80,"packet_loss":0,"throughput_mbps":100,"status":"healthy"}]',
        encoding="utf-8",
    )

    monkeypatch.setenv("EXECUTOR_STATE_PATH", str(state_path))
    monkeypatch.setenv("EXECUTOR_HISTORY_PATH", str(history_path))
    monkeypatch.setenv("EXECUTOR_VALID_ROUTES", "aws-node")

    app = create_app(APIConfig(storage_path=str(metrics_path), nodes_storage_path=str(nodes_path)))
    client = TestClient(app)

    response = client.post("/execute-route")

    assert response.status_code == 200
    assert response.json()["executed"] is True
    assert response.json()["active_route"] == "aws-node"
