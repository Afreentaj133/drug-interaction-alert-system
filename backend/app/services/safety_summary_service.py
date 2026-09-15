import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.patient import Patient
from backend.app.models.medication_safety_report import MedicationSafetyReport
from backend.app.schemas.safety_report_schema import ClinicalSafetyReportResponse
from backend.app.services.polypharmacy_service import polypharmacy_service
from backend.app.utils.logger import logger

class SafetySummaryService:
    @staticmethod
    def generate_patient_safety_summary(db: Session, patient: Patient) -> ClinicalSafetyReportResponse:
        """
        Compiles an end-to-end AI-assisted Clinical Medication Safety Summary combining
        patient clinical history, active medications, document findings, multi-drug pair screening,
        SHAP explainability, and clinical disclaimers.
        """
        # 1. Run polypharmacy multi-drug screening
        screening_res = polypharmacy_service.screen_patient_medications(db, patient)

        # 2. Extract active and previous medications
        active_meds = []
        previous_meds = []
        for m in patient.medications:
            item = {
                "drug_name": m.drug_name,
                "dose": m.dose or "Not specified",
                "frequency": m.frequency or "Not specified",
                "route": m.route or "Oral",
                "status": m.status,
                "source": m.source,
                "notes": m.notes or ""
            }
            if m.status == "Current":
                active_meds.append(item)
            else:
                previous_meds.append(item)

        # 3. Extract document findings
        doc_findings = []
        for doc in patient.documents:
            doc_findings.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "document_date": doc.document_date,
                "extracted_meds_count": len(doc.extracted_medications)
            })

        # 4. Synthesize clinical action items
        action_items = []
        if screening_res.major_risk_count > 0:
            action_items.append(
                f"Urgent Pharmacotherapy Review: {screening_res.major_risk_count} Major-severity interaction pair(s) detected. Evaluate alternative therapeutic agents or adjust dosing intervals."
            )
        if screening_res.moderate_risk_count > 0:
            action_items.append(
                f"Clinical Monitoring Warranted: {screening_res.moderate_risk_count} Moderate interaction pair(s) identified. Monitor clinical signs, adverse symptoms, and relevant biochemical markers."
            )
        if screening_res.mechanism_warnings:
            for w in screening_res.mechanism_warnings:
                action_items.append(f"Cumulative Regimen Warning: {w}")
        if not action_items:
            action_items.append(
                "No major or moderate drug-drug interactions detected across current active medications under standard predictive thresholds. Continue routine clinical monitoring."
            )

        # Parse conditions and allergies into clean lists
        conditions_list = [c.strip() for c in (patient.conditions or "").split(",") if c.strip()]
        allergies_list = [a.strip() for a in (patient.allergies or "").split(",") if a.strip()]

        report_response = ClinicalSafetyReportResponse(
            patient_id=patient.patient_id,
            patient_name=patient.name,
            age=patient.age,
            sex=patient.sex,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            known_conditions=conditions_list,
            known_allergies=allergies_list,
            active_medications=active_meds,
            previous_medications=previous_meds,
            document_findings=doc_findings,
            total_screened_pairs=screening_res.total_pairs_screened,
            risk_breakdown={
                "Major": screening_res.major_risk_count,
                "Moderate": screening_res.moderate_risk_count,
                "Minor": screening_res.minor_risk_count,
                "Unsupported": screening_res.unsupported_count
            },
            high_priority_alerts=screening_res.major_pairs,
            moderate_alerts=screening_res.moderate_pairs,
            minor_interactions=screening_res.minor_pairs,
            unsupported_combinations=screening_res.unsupported_pairs,
            cumulative_hazard_signals=screening_res.mechanism_warnings,
            clinician_action_items=action_items,
            clinical_disclaimer=(
                "CLINICAL DECISION-SUPPORT PROTOTYPE NOTICE: This AI-generated safety summary is provided solely "
                "for clinical decision-support and educational review. It does not constitute autonomous medical advice "
                "or therapeutic instructions. Independent evaluation by a licensed healthcare professional is required."
            )
        )

        # Persist summary snapshot to database
        try:
            db_report = MedicationSafetyReport(
                patient_id=patient.id,
                summary_json=report_response.model_dump_json()
            )
            db.add(db_report)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist safety report to database: {e}")

        return report_response

safety_summary_service = SafetySummaryService()
