from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ExtractedMedicationResponse(BaseModel):
    id: int
    document_id: int
    extracted_text: str
    matched_drug_name: Optional[str] = None
    dosage: Optional[str] = None
    match_status: str # Matched, Corrected, Review Required, Uncataloged
    confidence: float
    is_confirmed: int
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: int
    patient_id: Optional[int] = None
    filename: str
    document_type: str
    file_size: int
    mime_type: str
    document_date: str
    processing_status: str
    created_at: datetime
    extracted_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class DocumentDetailResponse(DocumentResponse):
    raw_ocr_text: Optional[str] = None
    extracted_medications: List[ExtractedMedicationResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ConfirmedMedicationItem(BaseModel):
    id: Optional[int] = None # ExtractedMedication ID if existing
    drug_name: str
    dose: Optional[str] = None
    frequency: Optional[str] = "Once daily"
    route: Optional[str] = "Oral"
    status: Optional[str] = "Current"
    notes: Optional[str] = None

class ConfirmMedicationsRequest(BaseModel):
    patient_id: str # e.g. "DEMO-PT-1001" or target patient ID
    medications: List[ConfirmedMedicationItem]

class OcrExtractionResult(BaseModel):
    document_id: int
    filename: str
    document_date: str
    raw_text: str
    extracted_medications: List[ExtractedMedicationResponse]
