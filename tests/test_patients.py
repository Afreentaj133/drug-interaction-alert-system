import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

def test_patient_crud_and_medication_validation():
    with TestClient(app) as client:
        # 1. Get demo patients
        demo_resp = client.get("/api/patients/demo/list")
        assert demo_resp.status_code == 200
        demos = demo_resp.json()
        assert len(demos) >= 1
        assert any(d["patient_id"] == "DEMO-PT-1001" for d in demos)

        # 2. Create new patient
        new_pt_id = "TEST-PT-9999"
        create_resp = client.post("/api/patients", json={
            "patient_id": new_pt_id,
            "name": "Jane Test",
            "age": 52,
            "sex": "Female",
            "conditions": "Hypertension",
            "allergies": "Aspirin",
            "medical_history": "Mild hypertension",
            "surgeries": "None"
        })
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["patient_id"] == new_pt_id
        assert created["name"] == "Jane Test"

        # 3. Reject duplicate patient ID
        dup_resp = client.post("/api/patients", json={
            "patient_id": new_pt_id,
            "name": "Duplicate Jane",
        })
        assert dup_resp.status_code == 400

        # 4. Add valid cataloged medication (Metformin)
        med_resp = client.post(f"/api/patients/{new_pt_id}/medications", json={
            "drug_name": "Metformin",
            "dose": "500 mg",
            "frequency": "Twice daily",
            "route": "Oral",
            "status": "Current",
            "source": "Manual",
            "notes": "With meals"
        })
        assert med_resp.status_code == 201
        med_data = med_resp.json()
        assert med_data["drug_name"] == "Metformin"
        med_id = med_data["id"]

        # 5. Reject unknown / uncataloged drug name
        unknown_resp = client.post(f"/api/patients/{new_pt_id}/medications", json={
            "drug_name": "NonExistentDrugFake123",
            "dose": "10 mg"
        })
        assert unknown_resp.status_code == 404
        assert "not cataloged" in unknown_resp.json()["detail"].lower()

        # 6. Retrieve full patient details
        detail_resp = client.get(f"/api/patients/{new_pt_id}")
        assert detail_resp.status_code == 200
        details = detail_resp.json()
        assert len(details["medications"]) == 1
        assert details["medications"][0]["drug_name"] == "Metformin"

        # 7. Delete medication
        del_med = client.delete(f"/api/patients/{new_pt_id}/medications/{med_id}")
        assert del_med.status_code == 200

        # 8. Clean up test patient
        del_pt = client.delete(f"/api/patients/{new_pt_id}")
        assert del_pt.status_code == 200
