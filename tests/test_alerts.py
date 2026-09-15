from fastapi.testclient import TestClient
from backend.app.main import app

def test_alerts_and_dashboard_lifecycle():
    with TestClient(app) as client:
        # Initial check to generate an alert
        check_res = client.post("/api/interactions/check", json={"drug_a": "Warfarin", "drug_b": "Clarithromycin"})
        assert check_res.status_code == 200

        # Verify alert appears in /api/alerts
        alerts_res = client.get("/api/alerts")
        assert alerts_res.status_code == 200
        data = alerts_res.json()
        assert data["total"] >= 1
        alerts = data["alerts"]
        assert any("Warfarin" in a["drug_a"] or "Warfarin" in a["drug_b"] for a in alerts)

        # Test single alert detail
        target_alert = alerts[0]
        alert_detail = client.get(f"/api/alerts/{target_alert['id']}")
        assert alert_detail.status_code == 200
        assert alert_detail.json()["id"] == target_alert["id"]

        # Test severity filter
        major_res = client.get("/api/alerts?severity=Major")
        assert major_res.status_code == 200
        for item in major_res.json()["alerts"]:
            assert item["severity"].lower() == "major"

        # Verify dashboard statistics reflect actual database
        stats_res = client.get("/api/dashboard/stats")
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_checks"] >= 1
        assert stats["major_alerts"] >= 1

        # Delete alert
        del_res = client.delete(f"/api/alerts/{target_alert['id']}")
        assert del_res.status_code == 200

        # Verify 404 after deletion
        del_verify = client.get(f"/api/alerts/{target_alert['id']}")
        assert del_verify.status_code == 404
