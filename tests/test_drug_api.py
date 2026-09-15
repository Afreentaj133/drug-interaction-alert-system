from fastapi.testclient import TestClient
from backend.app.main import app

def test_drug_search_and_retrieval():
    with TestClient(app) as client:
        # Search for Warfarin
        res = client.get("/api/drugs/search?q=warfarin")
        assert res.status_code == 200
        drugs = res.json()
        assert len(drugs) > 0
        assert any(d["name"].lower() == "warfarin" for d in drugs)

        # Search with brand name
        res_brand = client.get("/api/drugs/search?q=coumadin")
        assert res_brand.status_code == 200
        drugs_brand = res_brand.json()
        assert len(drugs_brand) > 0

        # List all drugs
        res_all = client.get("/api/drugs?limit=50")
        assert res_all.status_code == 200
        all_drugs = res_all.json()
        assert len(all_drugs) >= 20

        # Fetch drug by valid ID
        first_id = all_drugs[0]["id"]
        res_detail = client.get(f"/api/drugs/{first_id}")
        assert res_detail.status_code == 200
        assert res_detail.json()["id"] == first_id

        # Fetch drug by invalid ID
        res_invalid = client.get("/api/drugs/999999")
        assert res_invalid.status_code == 404
