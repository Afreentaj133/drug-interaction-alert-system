from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.services.interaction_service import interaction_service
from backend.app.schemas.interaction_schema import InteractionRequest, InteractionResponse

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])

@router.post("/check", response_model=InteractionResponse)
def check_interaction(
    request: InteractionRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate potential drug-drug interaction between Drug A and Drug B.
    Runs chemical feature generation with RDKit, executes the ML framework,
    retrieves SHAP feature attribution, and generates a clinical decision-support response.
    """
    return interaction_service.check_interaction(db=db, request=request)
