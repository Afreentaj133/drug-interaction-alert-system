from ml.preprocessing.extract_features import (
    compute_single_drug_descriptors,
    get_morgan_fingerprint,
    create_pair_feature_vector,
    FEATURE_COLUMNS
)

def test_single_drug_descriptors():
    # Warfarin valid SMILES
    valid_smiles = "CC(=O)CC(C1=CC=CC=C1)C2=C(O)C3=CC=CC=C3OC2=O"
    desc = compute_single_drug_descriptors(valid_smiles)
    assert desc["molecular_weight"] > 300.0
    assert desc["h_donors"] >= 1
    assert desc["h_acceptors"] >= 3

    # Invalid SMILES recovery
    bad_smiles = "INVALID_SMILES_STRING@@"
    bad_desc = compute_single_drug_descriptors(bad_smiles)
    assert bad_desc["molecular_weight"] == 0.0
    assert bad_desc["h_donors"] == 0

def test_pairwise_feature_symmetry():
    drug_a = {
        "name": "Simvastatin",
        "smiles": "CCC(C)(C)C(=O)OC1CC(C)C=C2C1C(CCC2C)C(O)CC(=O)O",
        "molecular_weight": 418.57, "logp": 4.68, "tpsa": 72.83,
        "h_donors": 1, "h_acceptors": 5, "rotatable_bonds": 7, "heavy_atoms": 30, "ring_count": 2,
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "category": "Statin"
    }

    drug_b = {
        "name": "Clarithromycin",
        "smiles": "CC1CC(C(=O)C(C(C(=O)C(CC(C(C(C(C(=O)O1)C)OC2CC(C(C(O2)C)O)(C)OC)C)OC3C(C(CC(O3)C)N(C)C)O)(C)O)C)C)O",
        "molecular_weight": 747.95, "logp": 3.16, "tpsa": 180.4,
        "h_donors": 4, "h_acceptors": 14, "rotatable_bonds": 8, "heavy_atoms": 51, "ring_count": 3,
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "category": "Macrolide"
    }

    vec_ab = create_pair_feature_vector(drug_a, drug_b)
    vec_ba = create_pair_feature_vector(drug_b, drug_a)

    # Verify all expected columns exist
    for col in FEATURE_COLUMNS:
        assert col in vec_ab

    # Verify symmetry: (A, B) must equal (B, A)
    assert vec_ab == vec_ba

    # Verify specific interaction flags
    assert vec_ab["cyp_inhibitor_substrate_pair"] == 1
    assert vec_ab["both_cyp_substrates"] == 1
    assert vec_ab["tanimoto_similarity"] >= 0.0
    assert vec_ab["tanimoto_similarity"] <= 1.0
