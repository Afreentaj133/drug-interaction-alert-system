# Drug Interaction Alert System (DIAS) — Dataset Documentation

## 1. Provenance and Sources
The dataset utilized by the **Drug Interaction Alert System (DIAS)** is curated from scientifically validated public biomedical and cheminformatics repositories:
- **PubChem (NCBI)**: Canonical SMILES, IUPAC nomenclature, molecular formulae, and PubChem Compound Identifiers (CIDs).
- **DrugBank (Open Academic Data Subset)**: Drug classes, ATC classifications, target proteins, and clinical interaction descriptions.
- **ChEMBL**: Verified physicochemical properties (Exact Molecular Weight, ALogP, Topological Polar Surface Area, Hydrogen Bond Donors/Acceptors, Rotatable Bonds).
- **TWOSIDES / FDA FAERS**: Clinically reported adverse drug-drug interaction pairs and associated pharmacological risk mechanisms.

## 2. Regulatory and Licensing Compliance
- No proprietary, subscriber-only, or confidential patient health records are contained in this repository.
- Chemical identifiers and canonical SMILES are derived from public-domain and CC-BY databases (NCBI PubChem, ChEMBL).
- The dataset is designed specifically for research and educational decision-support modeling.

## 3. Dataset Schema

### Drugs Catalog (`drugs_database.csv`)
| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `drug_id` | Integer | Unique primary identifier | `1` |
| `name` | String | International Nonproprietary Name (INN) | `Warfarin` |
| `brand_names` | String | Common clinical brand names | `Coumadin, Jantoven` |
| `category` | String | Therapeutic / Pharmacological Class | `Anticoagulant` |
| `atc_code` | String | Anatomical Therapeutic Chemical code | `B01AA03` |
| `smiles` | String | Canonical SMILES structural representation | `CC(=O)CC(C1=CC=CC=C1)C2=C(O)C3=CC=CC=C3OC2=O` |
| `pubchem_cid` | Integer | PubChem Compound ID | `54678486` |
| `molecular_weight`| Float | Exact Molecular Weight (g/mol) | `308.33` |
| `logp` | Float | Octanol-water partition coefficient (LogP)| `2.7` |
| `tpsa` | Float | Topological Polar Surface Area (Å²) | `67.51` |
| `h_donors` | Integer | Number of Hydrogen Bond Donors | `1` |
| `h_acceptors` | Integer | Number of Hydrogen Bond Acceptors | `4` |
| `rotatable_bonds`| Integer | Number of rotatable bonds | `4` |
| `cyp_enzymes` | String | Primary hepatic CYP metabolic pathways | `CYP2C9, CYP3A4` |
| `cyp_inhibitor`| Integer | Binary indicator: CYP enzyme inhibitor | `0` |
| `cyp_substrate`| Integer | Binary indicator: CYP enzyme substrate | `1` |
| `qt_prolonging`| Integer | Binary indicator: Known Torsades/QT prolongation | `0` |
| `bleeding_risk`| Integer | Binary indicator: Intrinsic bleeding tendency | `1` |
| `serotonergic` | Integer | Binary indicator: Central serotonergic activity | `0` |
| `renal_risk` | Integer | Binary indicator: Nephrotoxicity / renal elimination | `0` |
| `clinician_note`| String | Evidence-based guidance / alternative review | `Consider direct oral anticoagulants (DOACs) under clinical evaluation` |

### Interaction Benchmark Matrix (`interactions_database.csv`)
| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `drug_a` | String | Drug A name | `Warfarin` |
| `drug_b` | String | Drug B name | `Aspirin` |
| `interaction` | Integer | Interaction binary label (1 = Interacting, 0 = Non-interacting) | `1` |
| `severity` | String | Severity classification (`Major`, `Moderate`, `Minor`, `None`) | `Major` |
| `mechanism` | String | Pharmacological mechanism (pharmacokinetic / pharmacodynamic) | `Additive antiplatelet and anticoagulant synergistic activity` |
| `clinical_risk`| String | Documented adverse event profile | `Significantly elevated risk of gastrointestinal and intracranial hemorrhage` |
| `recommendation`| String | Decision-support recommendation for clinicians | `Avoid concurrent administration or perform intensive clinical monitoring` |
| `potential_alternative` | String | Potential lower-risk alternative for clinician evaluation | `Acetaminophen/Paracetamol for mild pain; assess clinical suitability` |

## 4. Feature Extraction & Preprocessing Pipeline
1. Canonical SMILES strings are validated and parsed using **RDKit**.
2. Morgan fingerprints (radius 2, bit-length 2048, equivalent to **ECFP4**) are computed for each individual drug.
3. Pairwise Tanimoto similarity is calculated between Morgan fingerprint bitvectors.
4. Physicochemical descriptor deltas ($|\Delta \text{MolWt}|$, $|\Delta \text{LogP}|$, $|\Delta \text{TPSA}|$, etc.) and cross-products are assembled into the composite feature matrix.
5. Pharmacokinetic and pharmacodynamic synergy flags are integrated.
6. Negative non-interacting pairs are generated using constrained negative sampling, ensuring no train-test data leakage across drug entities.
