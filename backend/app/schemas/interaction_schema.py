from typing import List, Optional
from pydantic import BaseModel, Field

class InteractionRequest(BaseModel):
    drug_a: str = Field(..., description="Name of Drug A")
    drug_b: str = Field(..., description="Name of Drug B")

class ShapFeatureContribution(BaseModel):
    feature_name: str
    feature_label: str
    value: float
    shap_value: float
    impact: str # "Increases Risk" or "Decreases Risk"

class InteractionResponse(BaseModel):
    drug_a: str
    drug_b: str
    interaction_detected: bool
    risk_probability: float
    severity: str # "Major", "Moderate", "Minor"
    source: str # "Known clinical database" or "ML framework prediction"
    mechanism: str
    clinical_effect: str
    recommendation: str
    safer_alternative: Optional[str] = None
    explanation: List[str]
    shap_contributions: List[ShapFeatureContribution]
    clinical_disclaimer: str = (
        "DECISION-SUPPORT NOTICE: These predictive results are generated for educational and decision-support "
        "purposes only. Professional clinical verification by a qualified physician or pharmacist is required before "
        "making any prescribing or medication adjustment decisions."
    )
