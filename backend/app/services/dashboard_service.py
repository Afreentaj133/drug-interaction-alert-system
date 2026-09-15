from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.alert import Alert
from backend.app.schemas.dashboard_schema import DashboardStats, DrugFrequency, ActivityPoint

class DashboardService:
    @staticmethod
    def get_stats(db: Session) -> DashboardStats:
        total_checks = db.query(Alert).count()
        interactions_detected = db.query(Alert).filter(Alert.interaction_detected == 1).count()
        
        major_count = db.query(Alert).filter(Alert.severity.ilike("Major")).count()
        moderate_count = db.query(Alert).filter(Alert.severity.ilike("Moderate")).count()
        minor_count = db.query(Alert).filter(Alert.severity.ilike("Minor")).count()

        severity_distribution = {
            "Major": major_count,
            "Moderate": moderate_count,
            "Minor": minor_count
        }

        # Calculate top flagged drugs from actual alerts
        recent_alerts = db.query(Alert.drug_a, Alert.drug_b).filter(Alert.interaction_detected == 1).all()
        drug_counter = Counter()
        for a, b in recent_alerts:
            drug_counter[a] += 1
            drug_counter[b] += 1

        top_flagged = [
            DrugFrequency(drug_name=name, count=count)
            for name, count in drug_counter.most_common(5)
        ]

        # Recent activity over last 7 days from actual database
        today = datetime.now(timezone.utc).date()
        date_counts = {today - timedelta(days=i): 0 for i in range(6, -1, -1)}

        all_alerts = db.query(Alert.created_at).all()
        for (created_at,) in all_alerts:
            if created_at:
                alert_date = created_at.date()
                if alert_date in date_counts:
                    date_counts[alert_date] += 1

        recent_activity = [
            ActivityPoint(date=d.strftime("%b %d"), checks=c)
            for d, c in sorted(date_counts.items())
        ]

        from backend.app.models.patient import Patient
        from backend.app.models.patient_medication import PatientMedication
        from backend.app.models.medical_document import MedicalDocument

        total_patients = db.query(Patient).count()
        total_medications = db.query(PatientMedication).count()
        total_documents = db.query(MedicalDocument).count()

        return DashboardStats(
            total_checks=total_checks,
            interactions_detected=interactions_detected,
            major_alerts=major_count,
            moderate_alerts=moderate_count,
            minor_alerts=minor_count,
            severity_distribution=severity_distribution,
            top_flagged_drugs=top_flagged,
            recent_activity=recent_activity,
            total_patients=total_patients,
            total_medications_screened=total_medications,
            total_documents_processed=total_documents
        )

dashboard_service = DashboardService()
