from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.utils.config import settings
from backend.app.utils.logger import logger
from backend.app.database.init_db import init_db
from backend.app.api.endpoints import health, drugs, interactions, alerts, dashboard, model_info

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
LEGACY_STATIC = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Drug Interaction Alert System backend...")
    init_db()
    logger.info("Backend database initialized and verified.")
    yield
    logger.info("Shutting down Drug Interaction Alert System backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Clinical Decision-Support Prototype for Drug-Drug Interaction Review using Machine Learning, "
        "RDKit Cheminformatics, and SHAP Explainable AI."
    ),
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router)
app.include_router(drugs.router)
app.include_router(interactions.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(model_info.router)

# Mount Static Assets / Frontend Single Page Application
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})
        requested_file = FRONTEND_DIST / full_path
        if requested_file.is_file():
            return FileResponse(requested_file)
        return FileResponse(FRONTEND_DIST / "index.html")

elif LEGACY_STATIC.exists() and (LEGACY_STATIC / "index.html").exists():
    app.mount("/static", StaticFiles(directory=LEGACY_STATIC), name="static")

    @app.get("/")
    def serve_legacy_home():
        return FileResponse(LEGACY_STATIC / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
