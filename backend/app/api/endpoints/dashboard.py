from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.services.dashboard_service import dashboard_service
from backend.app.schemas.dashboard_schema import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """Retrieve actual aggregated database statistics for dashboard KPI cards and analytics charts."""
    return dashboard_service.get_stats(db=db)
