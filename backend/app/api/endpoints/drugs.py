from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.services.drug_service import drug_service
from backend.app.schemas.drug_schema import DrugOut, DrugSearchItem

router = APIRouter(prefix="/api/drugs", tags=["Drugs"])

@router.get("/search", response_model=List[DrugSearchItem])
def search_drugs(
    q: str = Query(default="", description="Search query string for drug name, brand, or category"),
    limit: int = Query(default=15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return drug_service.search_drugs(db=db, query=q, limit=limit)

@router.get("", response_model=List[DrugOut])
def list_drugs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    return drug_service.get_all_drugs(db=db, skip=skip, limit=limit)

@router.get("/{drug_id}", response_model=DrugOut)
def get_drug_details(drug_id: int, db: Session = Depends(get_db)):
    drug = drug_service.get_drug_by_id(db=db, drug_id=drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail=f"Drug with ID {drug_id} not found.")
    return drug
