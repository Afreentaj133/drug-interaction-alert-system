from fastapi.testclient import TestClient
from backend.app.main import app

def test_interaction_prediction_pipeline():
    with TestClient(app) as client:
        # Case 1: Severe anticoagulant + antiplatelet interaction
        res1 = client.post("/api/interactions/check", json={"drug_a": "Warfarin", "drug_b": "Aspirin"})
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["severity"] == "Major"
        assert data1["interaction_detected"] is True
        assert data1["risk_probability"] >= 0.70
        assert "hemorrhage" in data1["clinical_effect"].lower() or "bleeding" in data1["clinical_effect"].lower()
        assert len(data1["shap_contributions"]) > 0
        assert data1["clinical_disclaimer"] is not None

        # Case 2: CYP3A4 Statin + Macrolide rhabdomyolysis interaction
        res2 = client.post("/api/interactions/check", json={"drug_a": "Simvastatin", "drug_b": "Clarithromycin"})
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["severity"] == "Major"
        assert data2["interaction_detected"] is True
        assert "cyp3a4" in data2["mechanism"].lower()
        assert "rhabdomyolysis" in data2["clinical_effect"].lower() or "myopathy" in data2["clinical_effect"].lower()

        # Case 3: Clinically compatible low-risk pair
        res3 = client.post("/api/interactions/check", json={"drug_a": "Paracetamol", "drug_b": "Amoxicillin"})
        assert res3.status_code == 200
        data3 = res3.json()
        assert data3["severity"] == "Minor"
        assert data3["risk_probability"] < 0.50

        # Case 4: Symmetry check (A+B == B+A)
        res4 = client.post("/api/interactions/check", json={"drug_a": "Aspirin", "drug_b": "Warfarin"})
        assert res4.status_code == 200
        data4 = res4.json()
        assert data4["severity"] == data1["severity"]
        assert data4["risk_probability"] == data1["risk_probability"]
