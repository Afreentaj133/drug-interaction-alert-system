from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class PatientMedication(Base):
    __tablename__ = "patient_medications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    drug_name = Column(String(150), nullable=False, index=True) # Validated against Drug.name
    dose = Column(String(50), nullable=True) # e.g. "5 mg", "75 mg"
    frequency = Column(String(50), nullable=True) # e.g. "Once daily", "Twice daily"
    route = Column(String(50), nullable=True) # e.g. "Oral", "Intravenous"
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    status = Column(String(30), default="Current", nullable=False) # Current, Previous, Discontinued
    source = Column(String(50), default="Manual", nullable=False) # Manual, Prescription Upload, OCR Extracted
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    patient = relationship("Patient", back_populates="medications")
