from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.schemas.patient_schema import (
    PatientCreate, PatientUpdate, PatientResponse, PatientDetailResponse,
    PatientMedicationCreate, PatientMedicationResponse,
    PolypharmacyScreeningResponse
)
from backend.app.schemas.safety_report_schema import ClinicalSafetyReportResponse
from backend.app.services.patient_service import patient_service
from backend.app.services.polypharmacy_service import polypharmacy_service
from backend.app.services.safety_summary_service import safety_summary_service

router = APIRouter(prefix="/api/patients", tags=["Patients & Medication History"])

@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient clinical history record."""
    patient = patient_service.create_patient(db, payload)
    return PatientResponse(
        id=patient.id,
        patient_id=patient.patient_id,
        name=patient.name,
        age=patient.age,
        sex=patient.sex,
        conditions=patient.conditions,
        allergies=patient.allergies,
        medical_history=patient.medical_history,
        surgeries=patient.surgeries,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
        medications_count=0
    )

@router.get("", response_model=List[PatientResponse])
def list_patients(
    search: Optional[str] = Query(None, description="Search by patient ID or name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve list of patient records."""
    patients = patient_service.list_patients(db, search=search, skip=skip, limit=limit)
    results = []
    for p in patients:
        results.append(PatientResponse(
            id=p.id,
            patient_id=p.patient_id,
            name=p.name,
            age=p.age,
            sex=p.sex,
            conditions=p.conditions,
            allergies=p.allergies,
            medical_history=p.medical_history,
            surgeries=p.surgeries,
            created_at=p.created_at,
            updated_at=p.updated_at,
            medications_count=len(p.medications)
        ))
    return results

@router.get("/demo/list", response_model=List[PatientResponse])
def get_demo_patients(db: Session = Depends(get_db)):
    """Retrieve demonstration patient records."""
    patients = patient_service.list_patients(db, search="DEMO", limit=10)
    results = []
    for p in patients:
        results.append(PatientResponse(
            id=p.id,
            patient_id=p.patient_id,
            name=p.name,
            age=p.age,
            sex=p.sex,
            conditions=p.conditions,
            allergies=p.allergies,
            medical_history=p.medical_history,
            surgeries=p.surgeries,
            created_at=p.created_at,
            updated_at=p.updated_at,
            medications_count=len(p.medications)
        ))
    return results

@router.get("/{patient_id}", response_model=PatientDetailResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get full patient profile with complete medication history."""
    patient = patient_service.get_patient(db, patient_id)
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: str, payload: PatientUpdate, db: Session = Depends(get_db)):
    """Update patient clinical history fields."""
    patient = patient_service.update_patient(db, patient_id, payload)
    return PatientResponse(
        id=patient.id,
        patient_id=patient.patient_id,
        name=patient.name,
        age=patient.age,
        sex=patient.sex,
        conditions=patient.conditions,
        allergies=patient.allergies,
        medical_history=patient.medical_history,
        surgeries=patient.surgeries,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
        medications_count=len(patient.medications)
    )

@router.delete("/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    """Delete patient record and associated history."""
    return patient_service.delete_patient(db, patient_id)

@router.post("/{patient_id}/medications", response_model=PatientMedicationResponse, status_code=201)
def add_patient_medication(patient_id: str, payload: PatientMedicationCreate, db: Session = Depends(get_db)):
    """Add a validated medication to the patient's record."""
    med = patient_service.add_medication(db, patient_id, payload)
    return med

@router.delete("/{patient_id}/medications/{medication_id}")
def remove_patient_medication(patient_id: str, medication_id: int, db: Session = Depends(get_db)):
    """Remove a medication from the patient's history."""
    return patient_service.delete_medication(db, patient_id, medication_id)

@router.post("/{patient_id}/screen-medications", response_model=PolypharmacyScreeningResponse)
def screen_patient_medications(patient_id: str, db: Session = Depends(get_db)):
    """
    Screen all active current medications for a patient across all unique pairs
    using the validated Random Forest ML and RDKit ECFP4 cheminformatics pipeline.
    """
    patient = patient_service.get_patient(db, patient_id)
    return polypharmacy_service.screen_patient_medications(db, patient)

@router.get("/{patient_id}/safety-summary", response_model=ClinicalSafetyReportResponse)
def get_patient_safety_summary(patient_id: str, db: Session = Depends(get_db)):
    """
    Generate an AI-assisted Clinical Medication Safety Summary combining patient history,
    active medications, document findings, multi-drug pair screening, and SHAP explanations.
    """
    patient = patient_service.get_patient(db, patient_id)
    return safety_summary_service.generate_patient_safety_summary(db, patient)
