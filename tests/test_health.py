from fastapi.testclient import TestClient
from backend.app.main import app

def test_health_endpoints():
    with TestClient(app) as client:
        res1 = client.get("/health")
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["status"] == "healthy"
        assert "Drug Interaction Alert System" in data1["service"]

        res2 = client.get("/api/health")
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["status"] == "healthy"
