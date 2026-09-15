from pathlib import Path
import os
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ML_DIR = BASE_DIR / "ml"

class Settings(BaseModel):
    PROJECT_NAME: str = "Drug Interaction Alert System (DIAS)"
    PROJECT_VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database: SQLite fallback for local development, PostgreSQL for production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'drug_interaction.db'}"
    )
    
    # CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "*"
    ]
    
    # Model Artifact Paths
    MODEL_PATH: Path = ML_DIR / "models" / "champion_model.joblib"
    SHAP_EXPLAINER_PATH: Path = ML_DIR / "models" / "shap_explainer.joblib"
    DRUGS_DATA_PATH: Path = ML_DIR / "data" / "drugs_database.csv"
    INTERACTIONS_DATA_PATH: Path = ML_DIR / "data" / "interactions_database.csv"
    METRICS_DATA_PATH: Path = ML_DIR / "evaluation" / "metrics.json"

settings = Settings()
