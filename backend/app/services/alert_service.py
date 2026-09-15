from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.alert import Alert
from backend.app.schemas.alert_schema import AlertOut

class AlertService:
    @staticmethod
    def get_alerts(
        db: Session,
        severity: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[int, List[AlertOut]]:
        query = db.query(Alert)

        if severity and severity.lower() != "all":
            query = query.filter(Alert.severity.ilike(severity))

        if search:
            clean_s = search.strip().lower()
            query = query.filter(
                or_(
                    Alert.drug_a.ilike(f"%{clean_s}%"),
                    Alert.drug_b.ilike(f"%{clean_s}%"),
                    Alert.clinical_effect.ilike(f"%{clean_s}%")
                )
            )

        total = query.count()
        alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
        return total, [AlertOut.model_validate(a) for a in alerts]

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[AlertOut]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        return AlertOut.model_validate(alert) if alert else None

    @staticmethod
    def delete_alert(db: Session, alert_id: int) -> bool:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            db.delete(alert)
            db.commit()
            return True
        return False

alert_service = AlertService()
