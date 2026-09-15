from typing import List, Dict
from pydantic import BaseModel

class DrugFrequency(BaseModel):
    drug_name: str
    count: int

class ActivityPoint(BaseModel):
    date: str
    checks: int

class DashboardStats(BaseModel):
    total_checks: int
    interactions_detected: int
    major_alerts: int
    moderate_alerts: int
    minor_alerts: int
    severity_distribution: Dict[str, int]
    top_flagged_drugs: List[DrugFrequency]
    recent_activity: List[ActivityPoint]
