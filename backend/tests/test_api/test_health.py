"""Health check API tests."""

from fastapi.testclient import TestClient


def test_read_root(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_docs(client: TestClient) -> None:
    """Test API docs endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200
