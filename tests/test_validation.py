from fastapi.testclient import TestClient
from backend.app.main import app

def test_validation_rules():
    with TestClient(app) as client:
        # 1. Empty input
        res_empty = client.post("/api/interactions/check", json={"drug_a": "", "drug_b": "Warfarin"})
        assert res_empty.status_code == 400
        assert "must be specified" in res_empty.json()["detail"].lower()

        # 2. Duplicate same drug
        res_dup = client.post("/api/interactions/check", json={"drug_a": "Warfarin", "drug_b": "Warfarin"})
        assert res_dup.status_code == 400
        assert "duplicate" in res_dup.json()["detail"].lower()

        # 3. Case-insensitive duplicate (e.g. warfarin + WARFARIN)
        res_dup_case = client.post("/api/interactions/check", json={"drug_a": "warfarin", "drug_b": "WARFARIN"})
        assert res_dup_case.status_code == 400
        assert "duplicate" in res_dup_case.json()["detail"].lower()

        # 4. Unknown drug
        res_unknown = client.post("/api/interactions/check", json={"drug_a": "Warfarin", "drug_b": "FictionalMed123"})
        assert res_unknown.status_code == 404
        assert "not cataloged" in res_unknown.json()["detail"].lower()
