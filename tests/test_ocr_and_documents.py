import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

def test_document_validation_and_ocr_pipeline():
    with TestClient(app) as client:
        # 1. Reject invalid file extension (.exe)
        bad_ext_resp = client.post(
            "/api/documents/upload",
            files={"file": ("malware.exe", b"MZDummyContent", "application/x-dosexec")}
        )
        assert bad_ext_resp.status_code == 400
        assert "unsupported file type" in bad_ext_resp.json()["detail"].lower()

        # 2. Reject empty file (0 bytes)
        empty_file_resp = client.post(
            "/api/documents/upload",
            files={"file": ("empty.png", b"", "image/png")}
        )
        assert empty_file_resp.status_code == 400
        assert "empty" in empty_file_resp.json()["detail"].lower()

        # 3. Load synthetic demo sample prescription
        demo_sample_resp = client.post("/api/documents/demo-sample", data={"patient_id": "DEMO-PT-1001"})
        assert demo_sample_resp.status_code == 201
        data = demo_sample_resp.json()
        assert data["document_id"] > 0
        assert data["document_date"] != "Date not detected"
        assert len(data["extracted_medications"]) >= 3

        # Verify that extracted items are unconfirmed by default (is_confirmed == 0)
        for med in data["extracted_medications"]:
            assert med["is_confirmed"] == 0
            assert med["match_status"] in ["Matched", "Corrected", "Review Required"]
            assert med["confidence"] > 0.0

        doc_id = data["document_id"]

        # 4. Clinician confirmation: Confirm extracted medications to patient DEMO-PT-1001
        confirm_resp = client.post(
            f"/api/documents/{doc_id}/confirm-medications",
            json={
                "patient_id": "DEMO-PT-1001",
                "medications": [
                    {"id": data["extracted_medications"][0]["id"], "drug_name": "Warfarin", "dose": "5 mg", "frequency": "Once daily"}
                ]
            }
        )
        assert confirm_resp.status_code == 200
        confirm_data = confirm_resp.json()
        assert confirm_data["status"] == "success"
        assert confirm_data["confirmed_count"] >= 1

        # 5. Verify PDF upload with valid PDF structure
        import pypdf
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=200, height=200)
        stream = io.BytesIO()
        writer.write(stream)
        pdf_bytes = stream.getvalue()

        pdf_upload = client.post(
            "/api/documents/upload",
            files={"file": ("test_prescription.pdf", pdf_bytes, "application/pdf")},
            data={"patient_id": "DEMO-PT-1001"}
        )
        assert pdf_upload.status_code == 201
        assert pdf_upload.json()["filename"] == "test_prescription.pdf"
