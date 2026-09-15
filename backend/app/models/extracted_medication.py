from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class ExtractedMedication(Base):
    __tablename__ = "extracted_medications"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("medical_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    extracted_text = Column(String(255), nullable=False) # e.g. "Tab Warfarin 5mg OD"
    matched_drug_name = Column(String(150), nullable=True) # Normalized canonical drug name
    dosage = Column(String(50), nullable=True) # e.g. "5 mg"
    match_status = Column(String(50), default="Review Required", nullable=False) # Matched, Corrected, Review Required, Uncataloged
    confidence = Column(Float, default=0.0, nullable=False) # 0.0 - 1.0
    is_confirmed = Column(Integer, default=0, nullable=False) # 0 = Pending clinician confirmation, 1 = Confirmed

    # Relationships
    document = relationship("MedicalDocument", back_populates="extracted_medications")
