"""
RDKit Molecular Feature Engineering Pipeline for Drug-Drug Interaction Prediction.
Extracts Morgan Fingerprints (ECFP4), calculates Tanimoto similarity,
physicochemical descriptor differentials, and pharmacological synergy indicators.
"""
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import Descriptors, Lipinski

FP_BITS = 1024
FP_RADIUS = 2

# Modern RDKit Fingerprint Generator
try:
    from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
    _generator = GetMorganGenerator(radius=FP_RADIUS, fpSize=FP_BITS)
    def get_morgan_fingerprint(smiles: str):
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return _generator.GetFingerprint(mol)
except Exception:
    from rdkit.Chem import AllChem
    def get_morgan_fingerprint(smiles: str, n_bits: int = FP_BITS, radius: int = FP_RADIUS):
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)

FEATURE_COLUMNS = [
    # Cheminformatics / Structural Features
    "tanimoto_similarity",
    "dice_similarity",
    "mw_diff",
    "mw_mean",
    "logp_diff",
    "logp_prod",
    "tpsa_diff",
    "tpsa_mean",
    "h_donors_diff",
    "h_acceptors_diff",
    "rotatable_bonds_diff",
    "heavy_atoms_diff",
    "ring_count_diff",
    
    # Pharmacological & Metabolic Interaction Flags
    "same_category",
    "both_cyp_substrates",
    "cyp_inhibitor_substrate_pair",
    "both_qt_prolonging",
    "both_bleeding_risk",
    "both_serotonergic",
    "both_renal_risk",
    "any_cyp_inhibitor",
    "any_qt_prolonging",
    "any_bleeding_risk",
    "any_serotonergic",
    "any_renal_risk"
]

FEATURE_LABELS = {
    "tanimoto_similarity": "Structural Fingerprint Similarity (Tanimoto ECFP4)",
    "dice_similarity": "Molecular Dice Similarity",
    "mw_diff": "Molecular Weight Difference",
    "mw_mean": "Mean Molecular Weight",
    "logp_diff": "Lipophilicity Difference (|ΔLogP|)",
    "logp_prod": "Lipophilicity Cross-Product",
    "tpsa_diff": "Polar Surface Area Difference (|ΔTPSA|)",
    "tpsa_mean": "Mean Polar Surface Area",
    "h_donors_diff": "Hydrogen Bond Donor Differential",
    "h_acceptors_diff": "Hydrogen Bond Acceptor Differential",
    "rotatable_bonds_diff": "Molecular Flexibility Differential",
    "heavy_atoms_diff": "Heavy Atom Count Differential",
    "ring_count_diff": "Aromatic/Aliphatic Ring Differential",
    "same_category": "Identical Pharmacological Therapeutic Class",
    "both_cyp_substrates": "Competitive Hepatic CYP Substrate Overlap",
    "cyp_inhibitor_substrate_pair": "Potent CYP Metabolic Inhibition / Substrate Pair",
    "both_qt_prolonging": "Additive Cardiac Ventricular Repolarization (QT Prolongation)",
    "both_bleeding_risk": "Additive Hemostatic / Bleeding Risk Synergy",
    "both_serotonergic": "Additive Central Serotonergic Hyperactivity Risk",
    "both_renal_risk": "Concurrent Nephrotoxic / Renal Clearance Strain",
    "any_cyp_inhibitor": "Presence of Hepatic CYP Enzyme Inhibitor",
    "any_qt_prolonging": "Presence of Proarrhythmic / QT Prolonging Agent",
    "any_bleeding_risk": "Presence of Anticoagulant or Antiplatelet Compound",
    "any_serotonergic": "Presence of Serotonergic Agent",
    "any_renal_risk": "Presence of Renally Eliminated / Nephrotoxic Agent"
}

def compute_single_drug_descriptors(smiles: str) -> Dict[str, float]:
    """Compute standard physicochemical descriptors for a drug molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {
            "molecular_weight": 0.0,
            "logp": 0.0,
            "tpsa": 0.0,
            "h_donors": 0,
            "h_acceptors": 0,
            "rotatable_bonds": 0,
            "heavy_atoms": 0,
            "ring_count": 0
        }
    
    return {
        "molecular_weight": float(Descriptors.MolWt(mol)),
        "logp": float(Descriptors.MolLogP(mol)),
        "tpsa": float(Descriptors.TPSA(mol)),
        "h_donors": int(Lipinski.NumHDonors(mol)),
        "h_acceptors": int(Lipinski.NumHAcceptors(mol)),
        "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
        "heavy_atoms": int(mol.GetNumHeavyAtoms()),
        "ring_count": int(Lipinski.RingCount(mol))
    }

def create_pair_feature_vector(drug_a: Dict[str, Any], drug_b: Dict[str, Any]) -> Dict[str, float]:
    """
    Construct a symmetric feature vector for a drug pair.
    Symmetric: (Drug A, Drug B) produces the exact same feature vector as (Drug B, Drug A).
    """
    smiles_a = str(drug_a.get("smiles", ""))
    smiles_b = str(drug_b.get("smiles", ""))
    
    fp_a = get_morgan_fingerprint(smiles_a)
    fp_b = get_morgan_fingerprint(smiles_b)
    
    if fp_a is not None and fp_b is not None:
        tanimoto = float(DataStructs.TanimotoSimilarity(fp_a, fp_b))
        dice = float(DataStructs.DiceSimilarity(fp_a, fp_b))
    else:
        tanimoto = 0.0
        dice = 0.0

    # Ensure physicochemical values are present
    mw_a = float(drug_a.get("molecular_weight", 0.0))
    mw_b = float(drug_b.get("molecular_weight", 0.0))
    logp_a = float(drug_a.get("logp", 0.0))
    logp_b = float(drug_b.get("logp", 0.0))
    tpsa_a = float(drug_a.get("tpsa", 0.0))
    tpsa_b = float(drug_b.get("tpsa", 0.0))
    hbd_a = int(drug_a.get("h_donors", 0))
    hbd_b = int(drug_b.get("h_donors", 0))
    hba_a = int(drug_a.get("h_acceptors", 0))
    hba_b = int(drug_b.get("h_acceptors", 0))
    rot_a = int(drug_a.get("rotatable_bonds", 0))
    rot_b = int(drug_b.get("rotatable_bonds", 0))
    hatom_a = int(drug_a.get("heavy_atoms", 0))
    hatom_b = int(drug_b.get("heavy_atoms", 0))
    ring_a = int(drug_a.get("ring_count", 0))
    ring_b = int(drug_b.get("ring_count", 0))

    # Pharmacological flags
    cyp_inh_a = int(drug_a.get("cyp_inhibitor", 0))
    cyp_inh_b = int(drug_b.get("cyp_inhibitor", 0))
    cyp_sub_a = int(drug_a.get("cyp_substrate", 0))
    cyp_sub_b = int(drug_b.get("cyp_substrate", 0))
    qt_a = int(drug_a.get("qt_prolonging", 0))
    qt_b = int(drug_b.get("qt_prolonging", 0))
    bleed_a = int(drug_a.get("bleeding_risk", 0))
    bleed_b = int(drug_b.get("bleeding_risk", 0))
    sero_a = int(drug_a.get("serotonergic", 0))
    sero_b = int(drug_b.get("serotonergic", 0))
    renal_a = int(drug_a.get("renal_risk", 0))
    renal_b = int(drug_b.get("renal_risk", 0))
    cat_a = str(drug_a.get("category", "")).strip().lower()
    cat_b = str(drug_b.get("category", "")).strip().lower()

    return {
        "tanimoto_similarity": round(tanimoto, 4),
        "dice_similarity": round(dice, 4),
        "mw_diff": round(abs(mw_a - mw_b), 2),
        "mw_mean": round((mw_a + mw_b) / 2.0, 2),
        "logp_diff": round(abs(logp_a - logp_b), 2),
        "logp_prod": round(logp_a * logp_b, 2),
        "tpsa_diff": round(abs(tpsa_a - tpsa_b), 2),
        "tpsa_mean": round((tpsa_a + tpsa_b) / 2.0, 2),
        "h_donors_diff": abs(hbd_a - hbd_b),
        "h_acceptors_diff": abs(hba_a - hba_b),
        "rotatable_bonds_diff": abs(rot_a - rot_b),
        "heavy_atoms_diff": abs(hatom_a - hatom_b),
        "ring_count_diff": abs(ring_a - ring_b),
        
        "same_category": int(cat_a == cat_b and cat_a != ""),
        "both_cyp_substrates": int(cyp_sub_a and cyp_sub_b),
        "cyp_inhibitor_substrate_pair": int((cyp_inh_a and cyp_sub_b) or (cyp_inh_b and cyp_sub_a)),
        "both_qt_prolonging": int(qt_a and qt_b),
        "both_bleeding_risk": int(bleed_a and bleed_b),
        "both_serotonergic": int(sero_a and sero_b),
        "both_renal_risk": int(renal_a and renal_b),
        "any_cyp_inhibitor": int(cyp_inh_a or cyp_inh_b),
        "any_qt_prolonging": int(qt_a or qt_b),
        "any_bleeding_risk": int(bleed_a or bleed_b),
        "any_serotonergic": int(sero_a or sero_b),
        "any_renal_risk": int(renal_a or renal_b)
    }

if __name__ == "__main__":
    test_a = {
        "name": "Warfarin",
        "smiles": "CC(=O)CC(C1=CC=CC=C1)C2=C(O)C3=CC=CC=C3OC2=O",
        "molecular_weight": 308.33, "logp": 2.7, "tpsa": 67.51,
        "h_donors": 1, "h_acceptors": 4, "rotatable_bonds": 4, "heavy_atoms": 23, "ring_count": 3,
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 0
    }
    test_b = {
        "name": "Aspirin",
        "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "molecular_weight": 180.16, "logp": 1.19, "tpsa": 63.6,
        "h_donors": 1, "h_acceptors": 3, "rotatable_bonds": 2, "heavy_atoms": 13, "ring_count": 1,
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1
    }
    feats = create_pair_feature_vector(test_a, test_b)
    print("Clean Test Warfarin + Aspirin Feature Vector:")
    for k, v in feats.items():
        print(f"  {k}: {v}")
