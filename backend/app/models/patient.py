from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. DEMO-PT-1001
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(20), nullable=True) # Male, Female, Other
    conditions = Column(Text, nullable=True) # e.g. "Hypertension, Atrial Fibrillation, Type 2 Diabetes"
    allergies = Column(Text, nullable=True) # e.g. "Penicillin, Sulfa drugs"
    medical_history = Column(Text, nullable=True) # General clinical background
    surgeries = Column(Text, nullable=True) # Surgical / procedural history
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    medications = relationship("PatientMedication", back_populates="patient", cascade="all, delete-orphan")
    documents = relationship("MedicalDocument", back_populates="patient", cascade="all, delete-orphan")
    safety_reports = relationship("MedicationSafetyReport", back_populates="patient", cascade="all, delete-orphan")
