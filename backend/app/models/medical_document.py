from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    document_type = Column(String(50), default="Prescription", nullable=False) # Prescription, Lab Report, Discharge Summary, Other
    file_size = Column(Integer, nullable=False, default=0) # Bytes
    mime_type = Column(String(100), nullable=False)
    document_date = Column(String(50), default="Date not detected", nullable=False)
    raw_ocr_text = Column(Text, nullable=True)
    processing_status = Column(String(50), default="Processed", nullable=False) # Processed, Pending, Failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    patient = relationship("Patient", back_populates="documents")
    extracted_medications = relationship("ExtractedMedication", back_populates="document", cascade="all, delete-orphan")
