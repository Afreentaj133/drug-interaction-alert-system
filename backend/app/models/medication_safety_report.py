from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class MedicationSafetyReport(Base):
    __tablename__ = "medication_safety_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    summary_json = Column(Text, nullable=False) # JSON-encoded safety summary
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    patient = relationship("Patient", back_populates="safety_reports")
