from sqlalchemy import Column, Integer, String, Float, Text
from backend.app.database.connection import Base

class Drug(Base):
    __tablename__ = "drugs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    brand_names = Column(String(250), nullable=True)
    category = Column(String(150), index=True, nullable=False)
    atc_code = Column(String(50), nullable=True)
    pubchem_cid = Column(Integer, nullable=True)
    smiles = Column(Text, nullable=False)
    formula = Column(String(100), nullable=True)
    
    # RDKit Physicochemical Descriptors
    molecular_weight = Column(Float, nullable=False, default=0.0)
    logp = Column(Float, nullable=False, default=0.0)
    tpsa = Column(Float, nullable=False, default=0.0)
    h_donors = Column(Integer, nullable=False, default=0)
    h_acceptors = Column(Integer, nullable=False, default=0)
    rotatable_bonds = Column(Integer, nullable=False, default=0)
    heavy_atoms = Column(Integer, nullable=False, default=0)
    ring_count = Column(Integer, nullable=False, default=0)

    # Pharmacological Risk Indicators
    cyp_inhibitor = Column(Integer, nullable=False, default=0)
    cyp_substrate = Column(Integer, nullable=False, default=0)
    qt_prolonging = Column(Integer, nullable=False, default=0)
    bleeding_risk = Column(Integer, nullable=False, default=0)
    serotonergic = Column(Integer, nullable=False, default=0)
    renal_risk = Column(Integer, nullable=False, default=0)
    
    clinician_note = Column(Text, nullable=True)
