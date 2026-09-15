from fastapi import APIRouter
from backend.app.utils.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
@router.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }
