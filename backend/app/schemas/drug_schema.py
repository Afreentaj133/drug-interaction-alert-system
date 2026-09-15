from typing import Optional, List
from pydantic import BaseModel

class DrugBase(BaseModel):
    name: str
    brand_names: Optional[str] = None
    category: str
    atc_code: Optional[str] = None
    pubchem_cid: Optional[int] = None
    smiles: str
    formula: Optional[str] = None
    molecular_weight: float
    logp: float
    tpsa: float
    h_donors: int
    h_acceptors: int
    rotatable_bonds: int
    heavy_atoms: int
    ring_count: int
    cyp_inhibitor: int
    cyp_substrate: int
    qt_prolonging: int
    bleeding_risk: int
    serotonergic: int
    renal_risk: int
    clinician_note: Optional[str] = None

class DrugOut(DrugBase):
    id: int

    class Config:
        from_attributes = True

class DrugSearchItem(BaseModel):
    id: int
    name: str
    category: str
    brand_names: Optional[str] = None
    smiles: str
    molecular_weight: float
    atc_code: Optional[str] = None

    class Config:
        from_attributes = True
