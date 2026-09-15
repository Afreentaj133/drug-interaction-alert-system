from sqlalchemy import Column, Integer, String, Text
from backend.app.database.connection import Base

class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, index=True)
    drug_a = Column(String(150), index=True, nullable=False)
    drug_b = Column(String(150), index=True, nullable=False)
    severity = Column(String(50), index=True, nullable=False) # Major, Moderate, Minor
    mechanism = Column(Text, nullable=False)
    clinical_risk = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    potential_alternative = Column(Text, nullable=True)
