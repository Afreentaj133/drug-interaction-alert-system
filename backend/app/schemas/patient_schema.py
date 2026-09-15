from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.interaction_schema import ShapFeatureContribution

class PatientMedicationBase(BaseModel):
    drug_name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = "Oral"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = "Current"
    source: str = "Manual"
    notes: Optional[str] = None

class PatientMedicationCreate(PatientMedicationBase):
    pass

class PatientMedicationResponse(PatientMedicationBase):
    id: int
    patient_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PatientBase(BaseModel):
    patient_id: str
    name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    conditions: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    surgeries: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    conditions: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    surgeries: Optional[str] = None

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    medications_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class PatientDetailResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    medications: List[PatientMedicationResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Polypharmacy Multi-Drug Screening Schemas
class PolypharmacyPairResult(BaseModel):
    drug_a: str
    drug_b: str
    interaction_detected: bool
    risk_probability: float
    severity: str # Major, Moderate, Minor, or Unsupported
    source: str
    mechanism: str
    clinical_effect: str
    recommendation: str
    safer_alternative: Optional[str] = None
    explanation: List[str] = []
    shap_contributions: List[ShapFeatureContribution] = []

class PolypharmacyScreeningResponse(BaseModel):
    patient_id: str
    patient_name: str
    total_medications: int
    total_pairs_screened: int
    major_risk_count: int
    moderate_risk_count: int
    minor_risk_count: int
    unsupported_count: int
    major_pairs: List[PolypharmacyPairResult] = []
    moderate_pairs: List[PolypharmacyPairResult] = []
    minor_pairs: List[PolypharmacyPairResult] = []
    unsupported_pairs: List[PolypharmacyPairResult] = []
    mechanism_warnings: List[str] = []
    disclaimer: str
