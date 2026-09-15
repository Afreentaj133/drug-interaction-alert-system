from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.medical_document import MedicalDocument
from backend.app.models.extracted_medication import ExtractedMedication
from backend.app.models.patient import Patient
from backend.app.schemas.document_schema import (
    DocumentResponse, DocumentDetailResponse, ExtractedMedicationResponse,
    ConfirmMedicationsRequest, OcrExtractionResult
)
from backend.app.schemas.patient_schema import PatientMedicationCreate
from backend.app.services.ocr_service import ocr_service
from backend.app.services.patient_service import patient_service
from backend.app.utils.logger import logger

router = APIRouter(prefix="/api/documents", tags=["Medical Documents & OCR Intake"])

@router.post("/upload", response_model=OcrExtractionResult, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a prescription, lab report, or discharge summary (JPG, PNG, PDF).
    Performs validation, OCR text extraction, and entity recognition against the drug catalog.
    """
    file_bytes = await file.read()
    filename = file.filename or "uploaded_document"
    content_type = file.content_type or "application/octet-stream"

    # Resolve optional patient foreign key
    db_patient_id = None
    if patient_id and patient_id.strip():
        patient = patient_service.get_patient(db, patient_id.strip())
        db_patient_id = patient.id

    doc = ocr_service.process_document(
        db=db,
        filename=filename,
        file_bytes=file_bytes,
        content_type=content_type,
        patient_id=db_patient_id
    )

    extracted_items = [
        ExtractedMedicationResponse(
            id=em.id,
            document_id=em.document_id,
            extracted_text=em.extracted_text,
            matched_drug_name=em.matched_drug_name,
            dosage=em.dosage,
            match_status=em.match_status,
            confidence=em.confidence,
            is_confirmed=em.is_confirmed
        )
        for em in doc.extracted_medications
    ]

    return OcrExtractionResult(
        document_id=doc.id,
        filename=doc.filename,
        document_date=doc.document_date,
        raw_text=doc.raw_ocr_text or "",
        extracted_medications=extracted_items
    )

@router.post("/demo-sample", response_model=OcrExtractionResult, status_code=201)
def load_demo_sample_prescription(
    patient_id: Optional[str] = Form("DEMO-PT-1001"),
    db: Session = Depends(get_db)
):
    """
    Load a synthetic demonstration prescription text and extract medications.
    Enables instant one-click demonstration without uploading real personal documents.
    """
    sample_text = (
        "ST. JUDE CLINICAL MEDICAL CENTER - OUTPATIENT PRESCRIPTION\n"
        "Date: 12/09/2026\n"
        "Patient ID: DEMO-PT-1001 | Age: 68 | Sex: M\n"
        "Diagnosis: Chronic Atrial Fibrillation with Hypertension\n\n"
        "Rx Prescribed Medications:\n"
        "1. Tab Warfarin 5 mg once daily in evening - Target INR 2.5\n"
        "2. Tab Aspirin 75 mg once daily after breakfast\n"
        "3. Tab Metformin 500 mg twice daily with meals\n"
        "4. Tab Amlodipine 5 mg once daily in morning\n"
        "5. Tab Clarithromycin 500 mg twice daily for respiratory infection\n\n"
        "Dr. V. Ramanathan, MD (Internal Medicine)\n"
        "Registration No: KMC-49210"
    )

    db_patient_id = None
    if patient_id:
        try:
            patient = patient_service.get_patient(db, patient_id)
            db_patient_id = patient.id
        except Exception:
            pass

    catalog_drugs = [d[0] for d in db.query(Patient.name).all()] # fallback
    from backend.app.models.drug import Drug
    catalog_drugs = [d[0] for d in db.query(Drug.name).all()]

    meds_found = ocr_service.parse_medications_from_text(sample_text, catalog_drugs)

    doc = MedicalDocument(
        patient_id=db_patient_id,
        filename="demo_prescription_cardiology.txt",
        document_type="Prescription",
        file_size=len(sample_text.encode("utf-8")),
        mime_type="text/plain",
        document_date="12/09/2026",
        raw_ocr_text=sample_text,
        processing_status="Processed"
    )
    db.add(doc)
    db.flush()

    extracted_items = []
    for med in meds_found:
        em = ExtractedMedication(
            document_id=doc.id,
            extracted_text=med["extracted_text"],
            matched_drug_name=med["matched_drug_name"],
            dosage=med["dosage"],
            match_status=med["match_status"],
            confidence=med["confidence"],
            is_confirmed=0
        )
        db.add(em)
        db.flush()
        extracted_items.append(ExtractedMedicationResponse(
            id=em.id,
            document_id=doc.id,
            extracted_text=em.extracted_text,
            matched_drug_name=em.matched_drug_name,
            dosage=em.dosage,
            match_status=em.match_status,
            confidence=em.confidence,
            is_confirmed=0
        ))

    db.commit()

    return OcrExtractionResult(
        document_id=doc.id,
        filename=doc.filename,
        document_date=doc.document_date,
        raw_text=doc.raw_ocr_text,
        extracted_medications=extracted_items
    )

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Retrieve document details, raw OCR text, and extracted medications."""
    doc = db.query(MedicalDocument).filter(MedicalDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Medical document record not found.")

    return DocumentDetailResponse(
        id=doc.id,
        patient_id=doc.patient_id,
        filename=doc.filename,
        document_type=doc.document_type,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        document_date=doc.document_date,
        processing_status=doc.processing_status,
        created_at=doc.created_at,
        extracted_count=len(doc.extracted_medications),
        raw_ocr_text=doc.raw_ocr_text,
        extracted_medications=[
            ExtractedMedicationResponse(
                id=em.id,
                document_id=em.document_id,
                extracted_text=em.extracted_text,
                matched_drug_name=em.matched_drug_name,
                dosage=em.dosage,
                match_status=em.match_status,
                confidence=em.confidence,
                is_confirmed=em.is_confirmed
            )
            for em in doc.extracted_medications
        ]
    )

@router.get("/patient/{patient_id}", response_model=List[DocumentResponse])
def get_patient_documents(patient_id: str, db: Session = Depends(get_db)):
    """Retrieve all uploaded documents for a specific patient."""
    patient = patient_service.get_patient(db, patient_id)
    docs = db.query(MedicalDocument).filter(MedicalDocument.patient_id == patient.id).order_by(MedicalDocument.created_at.desc()).all()
    return [
        DocumentResponse(
            id=d.id,
            patient_id=d.patient_id,
            filename=d.filename,
            document_type=d.document_type,
            file_size=d.file_size,
            mime_type=d.mime_type,
            document_date=d.document_date,
            processing_status=d.processing_status,
            created_at=d.created_at,
            extracted_count=len(d.extracted_medications)
        )
        for d in docs
    ]

@router.post("/{document_id}/confirm-medications")
def confirm_medications(
    document_id: int,
    payload: ConfirmMedicationsRequest,
    db: Session = Depends(get_db)
):
    """
    Clinician confirmation step: Transfer verified medications from the review screen
    into the patient's active medication list.
    """
    doc = db.query(MedicalDocument).filter(MedicalDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Medical document record not found.")

    patient = patient_service.get_patient(db, payload.patient_id)
    added_meds = []

    for item in payload.medications:
        if not item.drug_name or not item.drug_name.strip():
            continue

        try:
            med = patient_service.add_medication(
                db=db,
                patient_id_or_code=patient.patient_id,
                med_in=PatientMedicationCreate(
                    drug_name=item.drug_name,
                    dose=item.dose,
                    frequency=item.frequency or "Once daily",
                    route=item.route or "Oral",
                    status=item.status or "Current",
                    source="Prescription Upload",
                    notes=f"Extracted from document: {doc.filename}"
                )
            )
            added_meds.append(med.drug_name)

            # Mark extracted medication as confirmed if ID matches
            if item.id:
                em = db.query(ExtractedMedication).filter(ExtractedMedication.id == item.id).first()
                if em:
                    em.is_confirmed = 1
        except HTTPException as e:
            logger.warning(f"Could not confirm drug '{item.drug_name}': {e.detail}")

    # Associate document with patient if not already linked
    if not doc.patient_id:
        doc.patient_id = patient.id
    db.commit()

    return {
        "status": "success",
        "patient_id": patient.patient_id,
        "confirmed_count": len(added_meds),
        "confirmed_medications": added_meds,
        "message": f"Successfully transferred {len(added_meds)} confirmed medication(s) to patient {patient.patient_id}."
    }
