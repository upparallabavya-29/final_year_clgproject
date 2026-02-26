"""
Integration Tests for FastAPI Endpoints
Run: python -m pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient

# Must import from main
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_public_stats_summary():
    response = client.get("/api/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "total_users" in data


def test_encyclopedia_crops():
    response = client.get("/api/crops")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "crops" in data
    assert isinstance(data["crops"], list)
    assert len(data["crops"]) > 0
    assert isinstance(data["crops"][0], str)


def test_auth_protected_history():
    # Attempt to access protected route without token
    response = client.get("/api/history")
    assert response.status_code == 401
    assert "Authentication required." in response.json()["detail"]


@pytest.mark.skip(reason="Requires mocked database to avoid polluting real DB")
def test_full_auth_flow():
    # Registration
    reg_data = {
        "name": "Integration Test",
        "email": "integration@test.com",
        "password": "SecurePassword123"
    }
    response = client.post("/api/auth/register", json=reg_data)
    assert response.status_code == 200
    token = response.json().get("token")
    assert token is not None

    # History with auth
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/history", headers=headers)
    assert response.status_code == 200
    assert "total" in response.json()
