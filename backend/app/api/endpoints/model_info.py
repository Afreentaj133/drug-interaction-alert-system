import json
from fastapi import APIRouter
from backend.app.ml.predictor import predictor
from backend.app.utils.config import settings

router = APIRouter(prefix="/api/model", tags=["Model"])

@router.get("/info")
def get_model_information():
    """Retrieve authentic ML model metadata, benchmark evaluation results, and feature weights."""
    benchmark_data = {}
    if settings.METRICS_DATA_PATH.exists():
        try:
            with open(settings.METRICS_DATA_PATH, "r") as f:
                benchmark_data = json.load(f)
        except Exception:
            pass

    return {
        "framework_name": "Explainable Multi-Feature Drug Interaction Risk Prediction Framework",
        "active_champion_model": predictor.model_name,
        "feature_count": len(predictor.feature_columns),
        "threshold": predictor.threshold,
        "metadata": predictor.metadata,
        "benchmark_report": benchmark_data
    }
