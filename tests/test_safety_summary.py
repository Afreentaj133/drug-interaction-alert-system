import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

def test_patient_safety_summary_generation():
    with TestClient(app) as client:
        # 1. Generate safety summary for DEMO-PT-1001
        resp = client.get("/api/patients/DEMO-PT-1001/safety-summary")
        assert resp.status_code == 200
        summary = resp.json()

        # 2. Check patient clinical context
        assert summary["patient_id"] == "DEMO-PT-1001"
        assert len(summary["known_conditions"]) >= 1
        assert len(summary["known_allergies"]) >= 1
        assert len(summary["active_medications"]) >= 3

        # 3. Check screened pairs & risk breakdown
        assert summary["total_screened_pairs"] >= 3
        assert "Major" in summary["risk_breakdown"]
        assert "Moderate" in summary["risk_breakdown"]
        assert "Minor" in summary["risk_breakdown"]

        # 4. Check clinician action items and mandatory non-autonomous disclaimer
        assert len(summary["clinician_action_items"]) >= 1
        assert "CLINICAL DECISION-SUPPORT PROTOTYPE NOTICE" in summary["clinical_disclaimer"]
        assert "does not constitute autonomous medical advice" in summary["clinical_disclaimer"]
