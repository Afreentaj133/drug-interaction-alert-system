from pydantic import BaseModel, Field

class InteractionRequest(BaseModel):
    drug_a: str = Field(..., min_length=2)
    drug_b: str = Field(..., min_length=2)

class InteractionResponse(BaseModel):
    drug_a: str
    drug_b: str
    interaction_detected: bool
    source: str
    risk_probability: float
    severity: str
    mechanism: str
    clinical_effect: str
    recommendation: str
    safer_alternative: str
    explanation: list[str]