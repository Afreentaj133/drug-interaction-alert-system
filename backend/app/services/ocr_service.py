import io
import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from backend.app.models.drug import Drug
from backend.app.models.medical_document import MedicalDocument
from backend.app.models.extracted_medication import ExtractedMedication
from backend.app.utils.logger import logger

# Initialize RapidOCR engine lazily or globally
_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _ocr_engine = RapidOCR()
            logger.info("RapidOCR ONNX engine initialized successfully.")
        except Exception as e:
            logger.warning(f"Could not load RapidOCR engine: {e}")
            _ocr_engine = None
    return _ocr_engine

class OcrService:
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

    @staticmethod
    def validate_file(filename: str, file_size: int, content_type: str):
        """Validate file format, size, and integrity."""
        # 1. Extension check
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in OcrService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Supported formats are: JPG, JPEG, PNG, and PDF."
            )

        # 2. Size check
        if file_size <= 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")
        if file_size > OcrService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of 10 MB ({file_size / (1024*1024):.2f} MB)."
            )

    @staticmethod
    def extract_dates(text: str) -> str:
        """
        Extract date of medical document using regex patterns.
        Falls back to 'Date not detected' if no recognizable date is found.
        """
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', # DD/MM/YYYY or MM/DD/YYYY
            r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b', # YYYY-MM-DD
            r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b', # 15 Sep 2025
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4})\b' # September 15, 2025
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Date not detected"

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extract text from digital PDF using pypdf."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts).strip()
        except Exception as e:
            logger.warning(f"pypdf extraction failed or file is corrupted: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Unable to parse PDF file. The document may be corrupted or encrypted: {e}"
            )

    @staticmethod
    def extract_text_from_image(file_bytes: bytes) -> Tuple[str, float]:
        """Extract text and confidence from image using RapidOCR."""
        engine = get_ocr_engine()
        if not engine:
            return "OCR engine currently unavailable on host.", 0.0

        try:
            result, _ = engine(file_bytes)
            if not result:
                return "", 0.0

            lines = []
            confidences = []
            for item in result:
                # item: [box, text, score]
                if len(item) >= 3:
                    text = str(item[1]).strip()
                    score = float(item[2])
                    if text:
                        lines.append(text)
                        confidences.append(score)

            full_text = "\n".join(lines)
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            return full_text, round(avg_conf, 2)
        except Exception as e:
            logger.error(f"RapidOCR error: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"OCR processing failed for this image: {e}"
            )

    MEDICAL_KEYWORDS = {
        "rx", "tab", "tablet", "cap", "capsule", "inj", "injection", "syp", "syrup",
        "mg", "mcg", "g", "ml", "iu", "units", "od", "bd", "tds", "qid", "hs",
        "daily", "twice", "thrice", "dosage", "dose", "oral", "intravenous", "im", "iv",
        "dr", "doctor", "physician", "clinic", "clinical", "hospital", "patient",
        "prescription", "prescribed", "diagnosis", "history", "treatment", "medicine",
        "medication", "lab", "laboratory", "report", "discharge", "summary", "blood",
        "inr", "bp", "pulse", "pharmacy", "pharmacist", "formulation", "pathology", "drops"
    }

    NON_DRUG_TOKENS = {
        "ultimate", "python", "guide", "certificate", "certification", "completion",
        "course", "university", "college", "department", "degree", "diploma",
        "developer", "engineer", "engineering", "science", "information", "computer",
        "technology", "training", "institute", "school", "academy", "license",
        "programming", "software", "development", "data", "learning", "tutorial",
        "student", "participant", "instructor", "awarded", "achievement", "grade",
        "signature", "director", "coordinator", "president", "founder", "manager",
        "the", "and", "for", "with", "this", "that", "from", "have", "been", "successfully",
        "google", "microsoft", "amazon", "apple", "online", "verify", "issued", "credential"
    }

    @staticmethod
    def is_probable_medical_document(text: str, catalog_drugs: List[str]) -> bool:
        """Verify whether the text contains clinical indicators or exact catalog drug names."""
        lower_text = text.lower()
        words = set(re.findall(r'\b[a-z]{2,}\b', lower_text))
        
        # Check if any catalog drug is explicitly present
        for drug in catalog_drugs:
            if re.search(rf'\b{re.escape(drug.lower())}\b', lower_text):
                return True
                
        # Count medical keywords
        matching_keywords = words.intersection(OcrService.MEDICAL_KEYWORDS)
        return len(matching_keywords) >= 2

    @staticmethod
    def match_drug_candidate(token: str, catalog_drugs: List[str], has_dosage_or_prefix: bool = False) -> Tuple[Optional[str], str, float]:
        """
        Fuzzy match candidate token against catalog drugs with strict clinical thresholds.
        Returns: (matched_drug_name, status, confidence)
        """
        clean_token = re.sub(r'[^a-zA-Z]', '', token).strip().lower()
        if len(clean_token) < 3 or clean_token in OcrService.NON_DRUG_TOKENS:
            return None, "Uncataloged", 0.0

        best_match = None
        best_ratio = 0.0

        for drug_name in catalog_drugs:
            drug_lower = drug_name.lower()
            if clean_token == drug_lower:
                return drug_name, "Matched", 1.0

            ratio = SequenceMatcher(None, clean_token, drug_lower).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = drug_name

        # For fuzzy correction, require high similarity (>=0.82)
        # and require that the line has a dosage pattern or pharmaceutical prefix
        if best_ratio >= 0.82:
            return best_match, "Corrected", round(best_ratio, 2)
        elif best_ratio >= 0.78 and has_dosage_or_prefix:
            return best_match, "Review Required", round(best_ratio, 2)
        else:
            return None, "Uncataloged", round(best_ratio, 2)

    @staticmethod
    def parse_medications_from_text(raw_text: str, catalog_drugs: List[str]) -> List[Dict[str, Any]]:
        """
        Extract medication lines, dosage strengths, and map candidate names to catalog drugs.
        Only parses if the document shows clinical/medical characteristics.
        """
        if not OcrService.is_probable_medical_document(raw_text, catalog_drugs):
            logger.info("Document failed medical validation check (no clinical keywords or drug names).")
            return []

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        extracted_results = []
        seen_drugs = set()

        dosage_regex = re.compile(r'(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|units?|iu)\b)', re.IGNORECASE)
        prefix_regex = re.compile(r'^(?:tab|tablet|cap|capsule|syp|syrup|inj|injection)\.?\s*', re.IGNORECASE)

        for line in lines:
            dose_match = dosage_regex.search(line)
            has_prefix = bool(prefix_regex.search(line))
            dosage = dose_match.group(1).strip() if dose_match else None
            has_dosage_or_prefix = (dosage is not None) or has_prefix

            cleaned_line = prefix_regex.sub('', line)
            tokens = re.split(r'[\s,;:/\-]+', cleaned_line)

            for token in tokens:
                if len(token) < 3:
                    continue

                matched_name, status, conf = OcrService.match_drug_candidate(
                    token, catalog_drugs, has_dosage_or_prefix=has_dosage_or_prefix
                )

                if status in ["Matched", "Corrected", "Review Required"] and matched_name:
                    if matched_name.lower() in seen_drugs:
                        continue
                    seen_drugs.add(matched_name.lower())

                    extracted_results.append({
                        "extracted_text": line,
                        "matched_drug_name": matched_name,
                        "dosage": dosage or "Standard dose",
                        "match_status": status,
                        "confidence": conf,
                        "is_confirmed": 0
                    })
        return extracted_results

    @staticmethod
    def process_document(db: Session, filename: str, file_bytes: bytes, content_type: str, patient_id: Optional[int] = None) -> MedicalDocument:
        """Full pipeline: validate -> extract text -> date -> medications -> persist."""
        OcrService.validate_file(filename, len(file_bytes), content_type)

        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        raw_text = ""

        if ext == ".pdf":
            raw_text = OcrService.extract_text_from_pdf(file_bytes)
        else:
            raw_text, _ = OcrService.extract_text_from_image(file_bytes)

        if not raw_text.strip():
            raw_text = "[No readable text detected in uploaded document]"

        doc_date = OcrService.extract_dates(raw_text)

        # Retrieve catalog drugs for entity matching
        catalog_drugs = [d[0] for d in db.query(Drug.name).all()]
        meds_found = OcrService.parse_medications_from_text(raw_text, catalog_drugs)

        doc = MedicalDocument(
            patient_id=patient_id,
            filename=filename,
            document_type="Prescription",
            file_size=len(file_bytes),
            mime_type=content_type,
            document_date=doc_date,
            raw_ocr_text=raw_text,
            processing_status="Processed"
        )
        db.add(doc)
        db.flush()

        for med in meds_found:
            em = ExtractedMedication(
                document_id=doc.id,
                extracted_text=med["extracted_text"],
                matched_drug_name=med["matched_drug_name"],
                dosage=med["dosage"],
                match_status=med["match_status"],
                confidence=med["confidence"],
                is_confirmed=0
            )
            db.add(em)

        db.commit()
        db.refresh(doc)
        return doc

ocr_service = OcrService()
