from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from backend.app.database.connection import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String(150), index=True, nullable=False)
    drug_b = Column(String(150), index=True, nullable=False)
    interaction_detected = Column(Integer, nullable=False, default=1)
    risk_probability = Column(Float, nullable=False)
    severity = Column(String(50), index=True, nullable=False) # Major, Moderate, Minor
    source = Column(String(100), nullable=False)
    mechanism = Column(Text, nullable=False)
    clinical_effect = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    safer_alternative = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True) # JSON-encoded list of clinical reasons
    shap_features = Column(Text, nullable=True) # JSON-encoded list of SHAP contributions
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
