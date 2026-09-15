from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.services.alert_service import alert_service
from backend.app.schemas.alert_schema import AlertOut, AlertListResponse

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", response_model=AlertListResponse)
def list_alerts(
    severity: Optional[str] = Query(default=None, description="Filter by severity (Major, Moderate, Minor)"),
    search: Optional[str] = Query(default=None, description="Filter by drug name"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total, alerts = alert_service.get_alerts(
        db=db, severity=severity, search=search, skip=skip, limit=limit
    )
    return AlertListResponse(total=total, alerts=alerts)

@router.get("/{alert_id}", response_model=AlertOut)
def get_alert_detail(alert_id: int, db: Session = Depends(get_db)):
    alert = alert_service.get_alert_by_id(db=db, alert_id=alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert record {alert_id} not found.")
    return alert

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    success = alert_service.delete_alert(db=db, alert_id=alert_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Alert record {alert_id} not found.")
    return {"status": "success", "message": f"Alert {alert_id} deleted."}
