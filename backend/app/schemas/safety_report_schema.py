from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.patient_schema import PolypharmacyPairResult

class ClinicalSafetyReportResponse(BaseModel):
    patient_id: str
    patient_name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    generated_at: str
    known_conditions: List[str] = []
    known_allergies: List[str] = []
    active_medications: List[Dict[str, Any]] = []
    previous_medications: List[Dict[str, Any]] = []
    document_findings: List[Dict[str, Any]] = []
    total_screened_pairs: int
    risk_breakdown: Dict[str, int]
    high_priority_alerts: List[PolypharmacyPairResult] = []
    moderate_alerts: List[PolypharmacyPairResult] = []
    minor_interactions: List[PolypharmacyPairResult] = []
    unsupported_combinations: List[PolypharmacyPairResult] = []
    cumulative_hazard_signals: List[str] = []
    clinician_action_items: List[str] = []
    clinical_disclaimer: str
