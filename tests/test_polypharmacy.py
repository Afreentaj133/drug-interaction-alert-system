import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

def test_polypharmacy_screening_pipeline():
    with TestClient(app) as client:
        # 1. Screen DEMO-PT-1001 (Warfarin, Metformin, Amlodipine)
        resp = client.post("/api/patients/DEMO-PT-1001/screen-medications")
        assert resp.status_code == 200
        data = resp.json()
        assert data["patient_id"] == "DEMO-PT-1001"
        assert data["total_medications"] >= 3
        # 3 medications => 3 pairs: (Warfarin, Metformin), (Warfarin, Amlodipine), (Metformin, Amlodipine)
        assert data["total_pairs_screened"] >= 3
        assert "disclaimer" in data

        # Verify all pairs have authentic model predictions and explanation
        all_screened = data["major_pairs"] + data["moderate_pairs"] + data["minor_pairs"]
        assert len(all_screened) == data["total_pairs_screened"]
        for p in all_screened:
            assert 0.0 <= p["risk_probability"] <= 1.0
            assert p["severity"] in ["Major", "Moderate", "Minor"]
            assert len(p["explanation"]) >= 1

        # 2. Add Aspirin to DEMO-PT-1001 as Current medication and re-screen
        med_resp = client.post("/api/patients/DEMO-PT-1001/medications", json={
            "drug_name": "Aspirin",
            "dose": "75 mg",
            "frequency": "Once daily",
            "status": "Current"
        })
        assert med_resp.status_code == 201
        aspirin_med_id = med_resp.json()["id"]

        try:
            # Re-screen: Warfarin + Aspirin is an established Major interaction!
            re_screen = client.post("/api/patients/DEMO-PT-1001/screen-medications")
            assert re_screen.status_code == 200
            re_data = re_screen.json()
            assert re_data["major_risk_count"] >= 1
            major_pair_names = [(p["drug_a"].lower(), p["drug_b"].lower()) for p in re_data["major_pairs"]]
            assert any(
                ("warfarin" in pair and "aspirin" in pair)
                for pair in major_pair_names
            )
            # Check mechanism warnings for cumulative bleeding risk
            assert any("bleeding" in w.lower() for w in re_data["mechanism_warnings"])
        finally:
            # Clean up added aspirin
            client.delete(f"/api/patients/DEMO-PT-1001/medications/{aspirin_med_id}")
