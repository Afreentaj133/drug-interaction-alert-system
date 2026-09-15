from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AlertOut(BaseModel):
    id: int
    drug_a: str
    drug_b: str
    interaction_detected: bool
    risk_probability: float
    severity: str
    source: str
    mechanism: str
    clinical_effect: str
    recommendation: str
    safer_alternative: Optional[str] = None
    explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    total: int
    alerts: List[AlertOut]
