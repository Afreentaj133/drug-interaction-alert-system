from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.drug import Drug
from backend.app.schemas.drug_schema import DrugOut, DrugSearchItem

class DrugService:
    @staticmethod
    def search_drugs(db: Session, query: str, limit: int = 15) -> List[DrugSearchItem]:
        """Search drugs by name, brand names, or category."""
        clean_q = query.strip().lower()
        if not clean_q:
            drugs = db.query(Drug).order_by(Drug.name.asc()).limit(limit).all()
        else:
            drugs = db.query(Drug).filter(
                or_(
                    Drug.name.ilike(f"%{clean_q}%"),
                    Drug.brand_names.ilike(f"%{clean_q}%"),
                    Drug.category.ilike(f"%{clean_q}%")
                )
            ).order_by(Drug.name.asc()).limit(limit).all()
            
        return [DrugSearchItem.model_validate(d) for d in drugs]

    @staticmethod
    def get_all_drugs(db: Session, skip: int = 0, limit: int = 100) -> List[DrugOut]:
        drugs = db.query(Drug).order_by(Drug.name.asc()).offset(skip).limit(limit).all()
        return [DrugOut.model_validate(d) for d in drugs]

    @staticmethod
    def get_drug_by_id(db: Session, drug_id: int) -> Optional[DrugOut]:
        drug = db.query(Drug).filter(Drug.id == drug_id).first()
        return DrugOut.model_validate(drug) if drug else None

    @staticmethod
    def get_drug_by_name(db: Session, name: str) -> Optional[Drug]:
        clean_name = name.strip().lower()
        return db.query(Drug).filter(Drug.name.ilike(clean_name)).first()

drug_service = DrugService()
