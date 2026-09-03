from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import initialize_database, save_alert, get_recent_alerts
from app.model_service import get_drug_names, predict_interaction
from app.schemas import InteractionRequest, InteractionResponse

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Drug Interaction Alert System",
    description="Educational ML-assisted drug interaction prototype",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def startup_event():
    initialize_database()

@app.get("/")
def serve_homepage():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Drug Interaction Alert System API is running"
    }

@app.get("/api/drugs")
def list_drugs():
    return {"drugs": get_drug_names()}

@app.post("/api/check-interaction", response_model=InteractionResponse)
def check_interaction(request: InteractionRequest):
    try:
        result = predict_interaction(request.drug_a, request.drug_b)

        save_alert(
            drug_a=result["drug_a"],
            drug_b=result["drug_b"],
            severity=result["severity"],
            risk_probability=result["risk_probability"],
            source=result["source"]
        )

        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.get("/api/recent-alerts")
def recent_alerts():
    return {"alerts": get_recent_alerts()}