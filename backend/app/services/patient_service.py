import random
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.patient import Patient
from backend.app.models.patient_medication import PatientMedication
from backend.app.models.drug import Drug
from backend.app.schemas.patient_schema import PatientCreate, PatientUpdate, PatientMedicationCreate
from backend.app.utils.logger import logger

class PatientService:
    @staticmethod
    def generate_demo_id() -> str:
        """Generate a synthetic demonstration patient identifier."""
        return f"DEMO-PT-{random.randint(1000, 9999)}"

    @staticmethod
    def create_patient(db: Session, patient_in: PatientCreate) -> Patient:
        # Check if patient_id already exists
        existing = db.query(Patient).filter(Patient.patient_id == patient_in.patient_id).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Patient ID '{patient_in.patient_id}' is already registered in the system."
            )

        patient = Patient(
            patient_id=patient_in.patient_id.strip(),
            name=patient_in.name.strip(),
            age=patient_in.age,
            sex=patient_in.sex,
            conditions=patient_in.conditions,
            allergies=patient_in.allergies,
            medical_history=patient_in.medical_history,
            surgeries=patient_in.surgeries
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def get_patient(db: Session, patient_id_or_code: str) -> Patient:
        """Find patient by internal DB id (if digit) or by patient_id code."""
        query = db.query(Patient)
        if patient_id_or_code.isdigit():
            patient = query.filter(or_(Patient.id == int(patient_id_or_code), Patient.patient_id == patient_id_or_code)).first()
        else:
            patient = query.filter(Patient.patient_id == patient_id_or_code).first()

        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient record '{patient_id_or_code}' not found."
            )
        return patient

    @staticmethod
    def list_patients(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Patient]:
        query = db.query(Patient)
        if search:
            s = f"%{search.strip()}%"
            query = query.filter(or_(Patient.patient_id.ilike(s), Patient.name.ilike(s), Patient.conditions.ilike(s)))
        return query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_patient(db: Session, patient_id_or_code: str, update_in: PatientUpdate) -> Patient:
        patient = PatientService.get_patient(db, patient_id_or_code)
        update_data = update_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def delete_patient(db: Session, patient_id_or_code: str):
        patient = PatientService.get_patient(db, patient_id_or_code)
        db.delete(patient)
        db.commit()
        return {"detail": f"Patient '{patient.patient_id}' and all associated records deleted."}

    @staticmethod
    def add_medication(db: Session, patient_id_or_code: str, med_in: PatientMedicationCreate) -> PatientMedication:
        patient = PatientService.get_patient(db, patient_id_or_code)
        drug_name_clean = med_in.drug_name.strip()

        # Strict validation against curated drug database
        drug = db.query(Drug).filter(Drug.name.ilike(drug_name_clean)).first()
        if not drug:
            raise HTTPException(
                status_code=404,
                detail=f"Medication '{drug_name_clean}' is not cataloged in the clinical formulary database. Please select a verified drug from the catalog."
            )

        medication = PatientMedication(
            patient_id=patient.id,
            drug_name=drug.name, # Use standardized canonical name
            dose=med_in.dose.strip() if med_in.dose else None,
            frequency=med_in.frequency.strip() if med_in.frequency else None,
            route=med_in.route.strip() if med_in.route else "Oral",
            start_date=med_in.start_date,
            end_date=med_in.end_date,
            status=med_in.status,
            source=med_in.source,
            notes=med_in.notes
        )
        db.add(medication)
        db.commit()
        db.refresh(medication)
        return medication

    @staticmethod
    def delete_medication(db: Session, patient_id_or_code: str, medication_id: int):
        patient = PatientService.get_patient(db, patient_id_or_code)
        med = db.query(PatientMedication).filter(
            PatientMedication.id == medication_id,
            PatientMedication.patient_id == patient.id
        ).first()
        if not med:
            raise HTTPException(status_code=404, detail="Medication entry not found for this patient.")
        db.delete(med)
        db.commit()
        return {"detail": "Medication removed from patient history."}

patient_service = PatientService()
