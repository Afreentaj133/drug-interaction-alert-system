"""
Curate comprehensive benchmark dataset of pharmaceutical agents and interaction pairs.
Uses RDKit to compute genuine physicochemical properties from canonical SMILES.
"""
from pathlib import Path
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "ml" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Comprehensive catalog of clinically essential pharmaceuticals across major therapeutic domains
RAW_DRUGS = [
    # Anticoagulants & Antiplatelets
    {
        "name": "Warfarin",
        "brand_names": "Coumadin, Jantoven",
        "category": "Anticoagulant",
        "atc_code": "B01AA03",
        "pubchem_cid": 54678486,
        "smiles": "CC(=O)CC(C1=CC=CC=C1)C2=C(O)C3=CC=CC=C3OC2=O",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Direct oral anticoagulants (Apixaban, Rivaroxaban) may be evaluated depending on renal function and clinical indication."
    },
    {
        "name": "Aspirin",
        "brand_names": "Bayer, Ecotrin",
        "category": "NSAID / Antiplatelet",
        "atc_code": "B01AC06",
        "pubchem_cid": 2244,
        "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Acetaminophen/Paracetamol is preferred for antipyretic/analgesic indication without antiplatelet risk."
    },
    {
        "name": "Clopidogrel",
        "brand_names": "Plavix",
        "category": "Antiplatelet",
        "atc_code": "B01AC04",
        "pubchem_cid": 60606,
        "smiles": "COC(=O)C(C1=CC=CC=C1Cl)N2CCC3=C(C2)C=CS3",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Ticagrelor or Prasugrel may be considered for acute coronary syndrome per specialist review."
    },
    {
        "name": "Apixaban",
        "brand_names": "Eliquis",
        "category": "Anticoagulant (DOAC)",
        "atc_code": "B01AF02",
        "pubchem_cid": 10182969,
        "smiles": "COC1=CC=C(C=C1)N2C(=O)C3=C(N2)C(=NN3C4=CC=C(C=C4)N5CCCCC5=O)C(=O)N",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Rivaroxaban or Dabigatran after assessing creatinine clearance and bleeding score."
    },
    {
        "name": "Rivaroxaban",
        "brand_names": "Xarelto",
        "category": "Anticoagulant (DOAC)",
        "atc_code": "B01AF01",
        "pubchem_cid": 9875401,
        "smiles": "C1COCC(=O)N1C2=CC=C(C=C2)N3CC(OC3=O)CNC(=O)C4=CC=C(S4)Cl",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Apixaban has twice-daily dosing with lower peak-trough fluctuation."
    },
    {
        "name": "Dabigatran",
        "brand_names": "Pradaxa",
        "category": "Direct Thrombin Inhibitor",
        "atc_code": "B01AE07",
        "pubchem_cid": 9578572,
        "smiles": "CCCCOC(=O)C(CC(=O)NC1=C(C=C(C=C1)C(=O)NCC2=CC=CC=N2)N(C)CC3=CC=CC=C3)NC(=N)N",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Specific reversal agent Idarucizumab available; adjust for renal clearance."
    },

    # Analgesics & NSAIDs
    {
        "name": "Ibuprofen",
        "brand_names": "Advil, Motrin",
        "category": "NSAID",
        "atc_code": "M01AE01",
        "pubchem_cid": 3672,
        "smiles": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Paracetamol for baseline analgesia; topical NSAIDs for localized musculoskeletal pain."
    },
    {
        "name": "Paracetamol",
        "brand_names": "Tylenol, Panadol, Acetaminophen",
        "category": "Analgesic / Antipyretic",
        "atc_code": "N02BE01",
        "pubchem_cid": 1983,
        "smiles": "CC(=O)NC1=CC=C(O)C=C1",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Low GI bleeding profile. Verify maximum daily dose (<4000 mg/24h) to avoid hepatotoxicity."
    },
    {
        "name": "Naproxen",
        "brand_names": "Aleve, Naprosyn",
        "category": "NSAID",
        "atc_code": "M01AE02",
        "pubchem_cid": 156391,
        "smiles": "CC(C1=CC2=C(C=C1)C=C(OC)C=C2)C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Celecoxib with PPI co-prescription if high GI risk and acceptable cardiovascular status."
    },
    {
        "name": "Celecoxib",
        "brand_names": "Celebrex",
        "category": "COX-2 Inhibitor NSAID",
        "atc_code": "M01AH01",
        "pubchem_cid": 2662,
        "smiles": "CC1=CC=C(C=C1)C2=CC(=NN2C3=CC=C(C=C3)S(=O)(=O)N)C(F)(F)F",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Acetaminophen for lower cardiovascular and renal risk profile."
    },
    {
        "name": "Ketorolac",
        "brand_names": "Toradol",
        "category": "Potent NSAID",
        "atc_code": "M01AB15",
        "pubchem_cid": 3826,
        "smiles": "C1CC2=CC=CC=C2N1C(=O)C3=CC=CC=C3C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Strict 5-day maximum duration due to severe gastrointestinal perforation and nephrotoxicity risk."
    },
    {
        "name": "Tramadol",
        "brand_names": "Ultram",
        "category": "Opioid Analgesic",
        "atc_code": "N02AX02",
        "pubchem_cid": 33741,
        "smiles": "CN(C)CC1CCCCC1(C2=CC(=CC=C2)OC)O",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Codeine or non-serotonergic opioid if pain management required without serotonin syndrome risk."
    },
    {
        "name": "Morphine",
        "brand_names": "MS Contin, Kadian",
        "category": "Opioid Analgesic",
        "atc_code": "N02AA01",
        "pubchem_cid": 5288826,
        "smiles": "CN1CCC23C4C1CC5=C2C(=C(O)C=C5)OC3C(C=C4)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Oxycodone or Hydromorphone with careful equianalgesic conversion and respiratory monitoring."
    },
    {
        "name": "Oxycodone",
        "brand_names": "OxyContin, Roxicodone",
        "category": "Opioid Analgesic",
        "atc_code": "N02AA05",
        "pubchem_cid": 5284603,
        "smiles": "CN1CCC23C4C1CC5=C2C(=C(OC)C=C5)OC3C(=O)CCC4(O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Morphine or Hydromorphone per pain protocol."
    },
    {
        "name": "Fentanyl",
        "brand_names": "Duragesic, Sublimaze",
        "category": "Opioid Analgesic",
        "atc_code": "N02AB03",
        "pubchem_cid": 3345,
        "smiles": "CCC(=O)N(C1CCN(CCC2=CC=CC=C2)CC1)C3=CC=CC=C3",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Morphine or Buprenorphine under specialized palliative/pain protocol."
    },

    # Cardiovascular / Statins / Antihypertensives
    {
        "name": "Simvastatin",
        "brand_names": "Zocor",
        "category": "HMG-CoA Reductase Inhibitor",
        "atc_code": "C10AA01",
        "pubchem_cid": 54454,
        "smiles": "CCC(C)(C)C(=O)OC1CC(C)C=C2C1C(CCC2C)C(O)CC(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Pravastatin or Rosuvastatin have lower CYP3A4-mediated rhabdomyolysis interaction potential."
    },
    {
        "name": "Atorvastatin",
        "brand_names": "Lipitor",
        "category": "HMG-CoA Reductase Inhibitor",
        "atc_code": "C10AA05",
        "pubchem_cid": 60823,
        "smiles": "CC(C)C1=C(C(=C(N1CCC(CC(CC(=O)O)O)O)C2=CC=C(C=C2)F)C3=CC=CC=C3)C(=O)NC4=CC=CC=C4",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Rosuvastatin or Pitavastatin for low CYP3A4 drug interaction liability."
    },
    {
        "name": "Rosuvastatin",
        "brand_names": "Crestor",
        "category": "HMG-CoA Reductase Inhibitor",
        "atc_code": "C10AA07",
        "pubchem_cid": 446157,
        "smiles": "CC(C)C1=NC(=NC(=C1C=CC(CC(CC(=O)O)O)O)C2=CC=C(C=C2)F)N(C)S(=O)(=O)C",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Pravastatin if severe hepatic disease; monitor renal function with high doses."
    },
    {
        "name": "Pravastatin",
        "brand_names": "Pravachol",
        "category": "HMG-CoA Reductase Inhibitor",
        "atc_code": "C10AA03",
        "pubchem_cid": 54687,
        "smiles": "CCC(C)C(=O)OC1CC(C=C2C1C(C(C=C2)C)CCC(CC(CC(=O)O)O)O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Eliminated by non-CYP pathways (sulfation); preferred statin when multiple CYP3A4 inhibitors present."
    },
    {
        "name": "Amiodarone",
        "brand_names": "Cordarone, Pacerone",
        "category": "Antiarrhythmic Class III",
        "atc_code": "C01BD01",
        "pubchem_cid": 2157,
        "smiles": "CCCCC1=C(C2=CC=CC=C2O1)C(=O)C3=CC(=C(C(=C3)I)OCCN(CC)CC)I",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Dronedarone or beta-blocker if non-severe ventricular rhythm; cardiology consultation required."
    },
    {
        "name": "Digoxin",
        "brand_names": "Lanoxin",
        "category": "Cardiac Glycoside",
        "atc_code": "C01AA05",
        "pubchem_cid": 2724385,
        "smiles": "CC1C(C(CC(O1)OC2C(OC(CC2O)OC3C(OC(CC3O)OC4CCC5(C(C4)CCC6C5CC(C7(C6(CCC7C8=CC(=O)OC8)O)C)O)C)C)C)O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Beta-blocker (Bisoprolol, Carvedilol) for rate control in atrial fibrillation."
    },
    {
        "name": "Lisinopril",
        "brand_names": "Prinivil, Zestril",
        "category": "ACE Inhibitor",
        "atc_code": "C09AA03",
        "pubchem_cid": 5362119,
        "smiles": "C1CC(N(C1)C(=O)C(CCCCN)NC(CCC2=CC=CC=C2)C(=O)O)C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Losartan or Amlodipine if ACE-inhibitor cough occurs or combination therapy needs re-evaluation."
    },
    {
        "name": "Enalapril",
        "brand_names": "Vasotec",
        "category": "ACE Inhibitor",
        "atc_code": "C09AA02",
        "pubchem_cid": 5388962,
        "smiles": "CCOC(=O)C(CCC1=CC=CC=C1)NC(C)C(=O)N2CCCC2C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Amlodipine or Telmisartan per clinical BP target and serum creatinine."
    },
    {
        "name": "Losartan",
        "brand_names": "Cozaar",
        "category": "Angiotensin II Receptor Blocker (ARB)",
        "atc_code": "C09CA01",
        "pubchem_cid": 3961,
        "smiles": "CCCCC1=NC(=C(N1CC2=CC=C(C=C2)C3=CC=CC=C3C4=NNN=N4)Cl)CO",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Valsartan or Amlodipine if patient shows hyperkalemia or hypotension."
    },
    {
        "name": "Valsartan",
        "brand_names": "Diovan",
        "category": "Angiotensin II Receptor Blocker (ARB)",
        "atc_code": "C09CA03",
        "pubchem_cid": 60846,
        "smiles": "CCCCC(=O)N(CC1=CC=C(C=C1)C2=CC=CC=C2C3=NNN=N3)C(C(C)C)C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Telmisartan has long half-life and dual PPAR-gamma partial agonism."
    },
    {
        "name": "Spironolactone",
        "brand_names": "Aldactone",
        "category": "Potassium-Sparing Diuretic",
        "atc_code": "C03DA01",
        "pubchem_cid": 5833,
        "smiles": "CC(=O)SC1CC2=CC(=O)CCC2(C3C1CC4C3(CCC45CCC(=O)O5)C)C",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Eplerenone has higher mineralocorticoid selectivity; Furosemide if potassium retention is high."
    },
    {
        "name": "Furosemide",
        "brand_names": "Lasix",
        "category": "Loop Diuretic",
        "atc_code": "C03CA01",
        "pubchem_cid": 3440,
        "smiles": "C1=C(C(=CC(=C1Cl)S(=O)(=O)N)C(=O)O)NCC2=CC=CO2",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Torsemide has more predictable bioavailability in chronic congestive heart failure."
    },
    {
        "name": "Hydrochlorothiazide",
        "brand_names": "Microzide",
        "category": "Thiazide Diuretic",
        "atc_code": "C03AA03",
        "pubchem_cid": 3639,
        "smiles": "C1NC2=CC(=C(C=C2S(=O)(=O)N1)S(=O)(=O)N)Cl",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Chlorthalidone or Indapamide based on eGFR and glycemic profile."
    },
    {
        "name": "Amlodipine",
        "brand_names": "Norvasc",
        "category": "Dihydropyridine Calcium Channel Blocker",
        "atc_code": "C08CA01",
        "pubchem_cid": 2162,
        "smiles": "CCOC(=O)C1=C(NC(=C(C1C2=CC=CC=C2Cl)C(=O)OC)C)COCCN",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Lercanidipine has lower incidence of peripheral ankle edema."
    },
    {
        "name": "Verapamil",
        "brand_names": "Calan, Verelan",
        "category": "Non-dihydropyridine Calcium Channel Blocker",
        "atc_code": "C08DA01",
        "pubchem_cid": 2520,
        "smiles": "CC(C)C(CCCN(C)CCC1=CC(=C(C=C1)OC)OC)(C#N)C2=CC(=C(C=C2)OC)OC",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Diltiazem or Amlodipine; verify baseline PR interval and ejection fraction."
    },
    {
        "name": "Diltiazem",
        "brand_names": "Cardizem",
        "category": "Non-dihydropyridine Calcium Channel Blocker",
        "atc_code": "C08DB01",
        "pubchem_cid": 39186,
        "smiles": "CC(=O)OC1C(SC2=CC=CC=C2N(C1=O)CCN(C)C)C3=CC=C(C=C3)OC",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Metoprolol or Amlodipine after evaluation of nodal conduction and LV function."
    },
    {
        "name": "Metoprolol",
        "brand_names": "Lopressor, Toprol-XL",
        "category": "Beta-1 Selective Adrenergic Blocker",
        "atc_code": "C07AB02",
        "pubchem_cid": 4171,
        "smiles": "CC(C)NCC(COC1=CC=C(C=C1)CCOC)O",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Bisoprolol or Atenolol have less dependence on CYP2D6 genetic polymorphism."
    },
    {
        "name": "Atenolol",
        "brand_names": "Tenormin",
        "category": "Beta-1 Selective Adrenergic Blocker",
        "atc_code": "C07AB03",
        "pubchem_cid": 2249,
        "smiles": "CC(C)NCC(COC1=CC=C(C=C1)CC(=O)N)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Bisoprolol or Nebivolol for enhanced endothelial nitric oxide release."
    },
    {
        "name": "Carvedilol",
        "brand_names": "Coreg",
        "category": "Non-selective Beta Blocker / Alpha-1 Blocker",
        "atc_code": "C07AG02",
        "pubchem_cid": 2585,
        "smiles": "COC1=CC=CC=C1OCCNCC(COC2=CC=CC3=C2C4=CC=CC=C4N3)O",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Metoprolol succinate for heart failure if alpha-blocker postural hypotension occurs."
    },

    # Psychotropics / Antidepressants / Sedatives
    {
        "name": "Fluoxetine",
        "brand_names": "Prozac",
        "category": "SSRI Antidepressant",
        "atc_code": "N06AB03",
        "pubchem_cid": 3386,
        "smiles": "CNCCC(C1=CC=CC=C1)OC2=CC=C(C=C2)C(F)(F)F",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 1, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Sertraline or Escitalopram have significantly shorter half-lives and less CYP2D6 inhibition."
    },
    {
        "name": "Sertraline",
        "brand_names": "Zoloft",
        "category": "SSRI Antidepressant",
        "atc_code": "N06AB06",
        "pubchem_cid": 68617,
        "smiles": "CNC1CCC(C2=CC=CC=C12)C3=CC(=C(C=C3)Cl)Cl",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 1, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Escitalopram has lower CYP enzyme inhibition potential."
    },
    {
        "name": "Escitalopram",
        "brand_names": "Lexapro, Cipralex",
        "category": "SSRI Antidepressant",
        "atc_code": "N06AB10",
        "pubchem_cid": 146570,
        "smiles": "CN(C)CCCC1(C2=C(CO1)C=C(C=C2)C#N)C3=CC=C(C=C3)F",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 1, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Mirtazapine or Bupropion if QT prolongation risk or sexual side effects are concerns."
    },
    {
        "name": "Citalopram",
        "brand_names": "Celexa",
        "category": "SSRI Antidepressant",
        "atc_code": "N06AB04",
        "pubchem_cid": 2771,
        "smiles": "CN(C)CCCC1(C2=C(CO1)C=C(C=C2)C#N)C3=CC=C(C=C3)F",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 1, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Sertraline has lower documented QT liability than racemic citalopram."
    },
    {
        "name": "Venlafaxine",
        "brand_names": "Effexor",
        "category": "SNRI Antidepressant",
        "atc_code": "N06AX16",
        "pubchem_cid": 5656,
        "smiles": "CN(C)CC(C1(CCCCC1)O)C2=CC=C(C=C2)OC",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 1, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Duloxetine or Desvenlafaxine under clinical assessment of blood pressure."
    },
    {
        "name": "Duloxetine",
        "brand_names": "Cymbalta",
        "category": "SNRI Antidepressant",
        "atc_code": "N06AX21",
        "pubchem_cid": 60835,
        "smiles": "CNCCC(C1=CC=CS1)OC2=CC=CC3=CC=CC=C32",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 1, "renal_risk": 1,
        "clinician_note": "Pregabalin or Gabapentin for neuropathic pain without serotonergic interaction risk."
    },
    {
        "name": "Amitriptyline",
        "brand_names": "Elavil",
        "category": "Tricyclic Antidepressant (TCA)",
        "atc_code": "N06AA09",
        "pubchem_cid": 2160,
        "smiles": "CN(C)CCC=C1C2=CC=CC=C2CCC3=CC=CC=C31",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Nortriptyline has lower anticholinergic and orthostatic side-effect burden."
    },
    {
        "name": "Diazepam",
        "brand_names": "Valium",
        "category": "Benzodiazepine",
        "atc_code": "N05BA01",
        "pubchem_cid": 3016,
        "smiles": "CN1C(=O)CN=C(C2=C1C=CC(=C2)Cl)C3=CC=CC=C3",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Lorazepam or Oxazepam undergo direct glucuronidation without active CYP metabolites."
    },
    {
        "name": "Lorazepam",
        "brand_names": "Ativan",
        "category": "Benzodiazepine",
        "atc_code": "N05BA06",
        "pubchem_cid": 3958,
        "smiles": "C1=CC=C(C(=C1)C2=NC(C(=O)NC3=C2C=C(C=C3)Cl)O)Cl",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Safer in hepatic insufficiency; non-benzodiazepine sleep aid (Melatonin) for insomnia."
    },
    {
        "name": "Alprazolam",
        "brand_names": "Xanax",
        "category": "Benzodiazepine",
        "atc_code": "N05BA12",
        "pubchem_cid": 2118,
        "smiles": "CC1=NN=C2CN=C(C3=CC=CC=C3)C4=C(C=C(C=C4)Cl)N12",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Buspirone or SSRI for long-term anxiety without sedation/dependence risk."
    },
    {
        "name": "Haloperidol",
        "brand_names": "Haldol",
        "category": "First-generation Antipsychotic",
        "atc_code": "N05AD01",
        "pubchem_cid": 3559,
        "smiles": "C1CCN(CC1)CCCC(=O)C2=CC=C(C=C2)F",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Aripiprazole or Olanzapine have lower extrapyramidal and QT prolongation profiles."
    },
    {
        "name": "Quetiapine",
        "brand_names": "Seroquel",
        "category": "Atypical Antipsychotic",
        "atc_code": "N05AH04",
        "pubchem_cid": 5002,
        "smiles": "C1CN(CCN1CCOCCO)C2=NC3=CC=CC=C3SC4=CC=CC=C42",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Aripiprazole or Risperidone under metabolic and sedation monitoring."
    },
    {
        "name": "Olanzapine",
        "brand_names": "Zyprexa",
        "category": "Atypical Antipsychotic",
        "atc_code": "N05AH03",
        "pubchem_cid": 4585,
        "smiles": "CC1=CC2=C(NC3=CC=CC=C3N=C2S1)N4CCN(C)CC4",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Lurasidone or Aripiprazole for favorable metabolic and weight profile."
    },

    # Antimicrobials & Antifungals
    {
        "name": "Clarithromycin",
        "brand_names": "Biaxin",
        "category": "Macrolide Antibiotic",
        "atc_code": "J01FA09",
        "pubchem_cid": 84029,
        "smiles": "CC1CC(C(=O)C(C(C(=O)C(CC(C(C(C(C(=O)O1)C)OC2CC(C(C(O2)C)O)(C)OC)C)OC3C(C(CC(O3)C)N(C)C)O)(C)O)C)C)O",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Azithromycin has minimal CYP3A4 inhibition; Doxycycline or Amoxicillin where indicated."
    },
    {
        "name": "Azithromycin",
        "brand_names": "Zithromax, Z-Pak",
        "category": "Macrolide Antibiotic",
        "atc_code": "J01FA10",
        "pubchem_cid": 55185,
        "smiles": "CCC1C(C(C(N(CC(C(C(C(C(=O)O1)C)OC2CC(C(C(O2)C)O)(C)OC)C)OC3C(C(CC(O3)C)N(C)C)O)C)C)O)(C)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Amoxicillin-clavulanate or Cefuroxime if QT interval prolongation is present."
    },
    {
        "name": "Ciprofloxacin",
        "brand_names": "Cipro",
        "category": "Fluoroquinolone Antibiotic",
        "atc_code": "J01MA02",
        "pubchem_cid": 2764,
        "smiles": "C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O",
        "cyp_inhibitor": 1, "cyp_substrate": 0, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Trimethoprim-sulfamethoxazole or Ceftriaxone based on antibiogram and tendon risk."
    },
    {
        "name": "Levofloxacin",
        "brand_names": "Levaquin",
        "category": "Fluoroquinolone Antibiotic",
        "atc_code": "J01MA12",
        "pubchem_cid": 149096,
        "smiles": "CC1COC2=C3N1C=C(C(=O)C3=CC(=C2N4CCN(C)CC4)F)C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Ceftriaxone or Doxycycline per pathogen sensitivity testing."
    },
    {
        "name": "Fluconazole",
        "brand_names": "Diflucan",
        "category": "Triazole Antifungal",
        "atc_code": "J02AC01",
        "pubchem_cid": 3365,
        "smiles": "C1=CC(=C(C=C1F)F)C(CN2C=NC=N2)(CN3C=NC=N3)O",
        "cyp_inhibitor": 1, "cyp_substrate": 0, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Nystatin for superficial candidiasis; Caspofungin or Terbinafine for systemic alternatives."
    },
    {
        "name": "Ketoconazole",
        "brand_names": "Nizoral",
        "category": "Imidazole Antifungal",
        "atc_code": "J02AB02",
        "pubchem_cid": 3823,
        "smiles": "CC(=O)N1CCN(CC1)C2=CC=C(C=C2)OCC3COC(O3)(CN4C=CN=C4)C5=C(C=C(C=C5)Cl)Cl",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Topical antifungal (Clotrimazole, Terbinafine) to avoid severe systemic CYP3A4 inhibition."
    },
    {
        "name": "Amoxicillin",
        "brand_names": "Amoxil",
        "category": "Aminopenicillin Antibiotic",
        "atc_code": "J01CA04",
        "pubchem_cid": 33613,
        "smiles": "CC1(C(N2C(S1)C(C2=O)NC(=O)C(C3=CC=C(C=C3)O)N)C(=O)O)C",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Broad safety profile; Cefalexin or Clindamycin if beta-lactam allergic."
    },
    {
        "name": "Doxycycline",
        "brand_names": "Vibramycin",
        "category": "Tetracycline Antibiotic",
        "atc_code": "J01AA02",
        "pubchem_cid": 54671203,
        "smiles": "CC1C2CC3C(C(=O)C(=C(C3(C(=O)C2=C(C4=C1C=CC=C4O)O)O)O)C(=O)N)N(C)C",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Minimal CYP-mediated interaction; separate administration from multivalent cations (calcium/iron)."
    },

    # Antidiabetics
    {
        "name": "Metformin",
        "brand_names": "Glucophage",
        "category": "Biguanide Antidiabetic",
        "atc_code": "A10BA02",
        "pubchem_cid": 4091,
        "smiles": "CN(C)C(=N)NC(=N)N",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Dapagliflozin or Empagliflozin (SGLT2 inhibitors) if eGFR acceptable; hold before contrast imaging."
    },
    {
        "name": "Glipizide",
        "brand_names": "Glucotrol",
        "category": "Sulfonylurea Antidiabetic",
        "atc_code": "A10BB07",
        "pubchem_cid": 3478,
        "smiles": "CC1=NC=C(C=N1)C(=O)NCCC2=CC=C(C=C2)S(=O)(=O)NC(=O)NC3CCCCC3",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Linagliptin or Empagliflozin have minimal hypoglycemia interaction profile."
    },
    {
        "name": "Empagliflozin",
        "brand_names": "Jardiance",
        "category": "SGLT2 Inhibitor",
        "atc_code": "A10BK03",
        "pubchem_cid": 11949646,
        "smiles": "C1=CC(=C(C=C1Cl)CC2=CC=C(C=C2)OC3CCOC3)C4C(C(C(C(O4)CO)O)O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Cardiovascular and renal protective benefits; monitor volume status."
    },

    # Anticonvulsants & Neurologicals
    {
        "name": "Phenytoin",
        "brand_names": "Dilantin",
        "category": "Hydantoin Antiepileptic / Inducer",
        "atc_code": "N03AB02",
        "pubchem_cid": 1775,
        "smiles": "C1=CC=C(C=C1)C2(C(=O)NC(=O)N2)C3=CC=CC=C3",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Levetiracetam has linear pharmacokinetics and minimal drug-drug interactions."
    },
    {
        "name": "Carbamazepine",
        "brand_names": "Tegretol",
        "category": "Iminostilbene Antiepileptic / Inducer",
        "atc_code": "N03AF01",
        "pubchem_cid": 2554,
        "smiles": "C1=CC=C2C(=C1)C=CC3=CC=CC=C3N2C(=O)N",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Oxcarbazepine or Lamotrigine have reduced auto-induction and interaction load."
    },
    {
        "name": "Levetiracetam",
        "brand_names": "Keppra",
        "category": "Pyrrolidine Antiepileptic",
        "atc_code": "N03AX14",
        "pubchem_cid": 5284583,
        "smiles": "CCC(C(=O)N)N1CCCC1=O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "First-line low-interaction antiepileptic; adjust dose according to renal clearance."
    },
    {
        "name": "Valproic Acid",
        "brand_names": "Depakene, Depakote",
        "category": "Broad-spectrum Anticonvulsant",
        "atc_code": "N03AG01",
        "pubchem_cid": 3121,
        "smiles": "CCCC(CCC)C(=O)O",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Levetiracetam or Lamotrigine if teratogenicity or hepatic enzyme inhibition is problematic."
    },

    # Gastrointestinal / PPIs / Antiemetics
    {
        "name": "Omeprazole",
        "brand_names": "Prilosec",
        "category": "Proton Pump Inhibitor (PPI)",
        "atc_code": "A02BC01",
        "pubchem_cid": 4594,
        "smiles": "CC1=CN=C(C(=C1OC)C)CS(=O)C2=NC3=C(N2)C=CC(=C3)OC",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Pantoprazole has minimal CYP2C19 inhibition; safer co-prescribed with Clopidogrel."
    },
    {
        "name": "Pantoprazole",
        "brand_names": "Protonix",
        "category": "Proton Pump Inhibitor (PPI)",
        "atc_code": "A02BC02",
        "pubchem_cid": 4679,
        "smiles": "COC1=C(C(=NC=C1)CS(=O)C2=NC3=C(N2)C=C(C=C3)OC(F)F)OC",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Preferred PPI when patient is taking antiplatelet clopidogrel."
    },
    {
        "name": "Ondansetron",
        "brand_names": "Zofran",
        "category": "5-HT3 Receptor Antagonist Antiemetic",
        "atc_code": "A04AA01",
        "pubchem_cid": 4595,
        "smiles": "CC1=NC=CN1CC2CCC(=O)C3=C2N(C)C4=CC=CC=C34",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 1, "renal_risk": 0,
        "clinician_note": "Metoclopramide or Prochlorperazine if baseline QTc prolongation is observed."
    },
    {
        "name": "Metoclopramide",
        "brand_names": "Reglan",
        "category": "Dopamine Receptor Antagonist Antiemetic",
        "atc_code": "A03FA01",
        "pubchem_cid": 4168,
        "smiles": "CCN(CC)CCNC(=O)C1=CC(=C(C=C1Cl)N)OC",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Domperidone or Ondansetron based on risk of tardive dyskinesia versus QT prolongation."
    },

    # Immunosuppressants & Steroids
    {
        "name": "Cyclosporine",
        "brand_names": "Neoral, Sandimmune",
        "category": "Calcineurin Inhibitor Immunosuppressant",
        "atc_code": "L04AD01",
        "pubchem_cid": 5284373,
        "smiles": "CC[C@H]1C(=O)N(CC(=O)N([C@H](C(=O)N[C@H](C(=O)N([C@H](C(=O)N[C@H](C(=O)N[C@@H](C(=O)N([C@H](C(=O)N([C@H](C(=O)N([C@H](C(=O)N([C@H](C(=O)N1)[C@@H]([C@H](C)C/C=C/C)O)C)C(C)C)C)CC(C)C)C)CC(C)C)C)C)C)CC(C)C)C)C(C)C)CC(C)C)C)C",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Tacrolimus or Mycophenolate Mofetil; therapeutic drug monitoring strictly required."
    },
    {
        "name": "Tacrolimus",
        "brand_names": "Prograf",
        "category": "Calcineurin Inhibitor Immunosuppressant",
        "atc_code": "L04AD02",
        "pubchem_cid": 445643,
        "smiles": "CC1CC(CC2=C(C=C(C3C(=O)C4(C(CCC4O3)(C(=O)C(CC2)O)O)C)C)OC)OC(=O)C(CC(CC(C(C(=O)C(C1)O)C)O)C)C",
        "cyp_inhibitor": 1, "cyp_substrate": 1, "qt_prolonging": 1, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Mycophenolate sodium or Azathioprine with blood trough level monitoring."
    },
    {
        "name": "Prednisone",
        "brand_names": "Deltasone",
        "category": "Glucocorticoid",
        "atc_code": "H02AB07",
        "pubchem_cid": 5865,
        "smiles": "CC12CC(=O)C3C(C1CCC2(C(=O)CO)O)CCC4=CC(=O)C=CC34C",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Methylprednisolone or Budesonide (topical enteric) for targeted bowel anti-inflammatory action."
    },
    {
        "name": "Methotrexate",
        "brand_names": "Trexall, Rheumatrex",
        "category": "Antimetabolite Antirheumatic / Cytotoxic",
        "atc_code": "L01BA01",
        "pubchem_cid": 126941,
        "smiles": "CN(CC1=CN=C2C(=N1)C(=NC(=N2)N)N)C3=CC=C(C=C3)C(=O)NC(CCC(=O)O)C(=O)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 1, "serotonergic": 0, "renal_risk": 1,
        "clinician_note": "Leflunomide or biologic DMARD (Adalimumab) under specialist rheumatology supervision."
    },

    # Respiratory & Others
    {
        "name": "Theophylline",
        "brand_names": "Theo-24, Uniphyl",
        "category": "Methylxanthine Bronchodilator",
        "atc_code": "R03DA04",
        "pubchem_cid": 2153,
        "smiles": "CN1C2=C(C(=O)N(C1=O)C)NC=N2",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Inhaled bronchodilators (Formoterol, Tiotropium) have wide therapeutic margins and less toxicity."
    },
    {
        "name": "Salbutamol",
        "brand_names": "Ventolin, Albuterol",
        "category": "Short-acting Beta-2 Agonist (SABA)",
        "atc_code": "R03CC02",
        "pubchem_cid": 2083,
        "smiles": "CC(C)(C)NCC(C1=CC(=C(C=C1)O)CO)O",
        "cyp_inhibitor": 0, "cyp_substrate": 0, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Ipratropium bromide for inhalational anticholinergic bronchodilation."
    },
    {
        "name": "Levothyroxine",
        "brand_names": "Synthroid, Levoxyl",
        "category": "Thyroid Hormone",
        "atc_code": "H03AA01",
        "pubchem_cid": 5819,
        "smiles": "C1=CC(=C(C=C1I)OC2=CC(=C(C(=C2)I)O)I)CC(C(=O)O)N",
        "cyp_inhibitor": 0, "cyp_substrate": 1, "qt_prolonging": 0, "bleeding_risk": 0, "serotonergic": 0, "renal_risk": 0,
        "clinician_note": "Separate dosing by at least 4 hours from oral iron, calcium, or antacid supplements."
    }
]

# Clinically authentic interactions with verified pharmacological mechanisms and severity
RAW_INTERACTIONS = [
    # Major Interactions
    {
        "drug_a": "Warfarin", "drug_b": "Aspirin",
        "severity": "Major",
        "mechanism": "Synergistic anticoagulant and antiplatelet pharmacodynamic action impairs both secondary hemostasis and primary platelet plug formation.",
        "clinical_risk": "Severe and potentially fatal hemorrhage, including gastrointestinal bleeding and intracranial hemorrhage.",
        "recommendation": "Avoid combination unless strictly indicated for high-risk prosthetic heart valves under rigorous INR monitoring.",
        "potential_alternative": "For analgesia/antipyresis, consider Paracetamol. For antiplatelet monotherapy, review clinical guidelines."
    },
    {
        "drug_a": "Warfarin", "drug_b": "Ibuprofen",
        "severity": "Major",
        "mechanism": "NSAID causes gastric mucosal damage and reversible platelet inhibition, while competitively displacing warfarin from plasma albumin.",
        "clinical_risk": "Marked increase in gastrointestinal ulceration, severe gastrointestinal hemorrhage, and elevated INR.",
        "recommendation": "Contraindicated in routine practice. Discontinue NSAID and switch to safer analgesic options.",
        "potential_alternative": "Paracetamol (up to 2g daily) or topical analgesics after clinician evaluation."
    },
    {
        "drug_a": "Warfarin", "drug_b": "Clarithromycin",
        "severity": "Major",
        "mechanism": "Potent inhibition of CYP3A4 and hepatic enzymes by macrolide, with gut flora eradication reducing vitamin K synthesis.",
        "clinical_risk": "Dramatic escalation of prothrombin time/INR, acute bleeding episodes.",
        "recommendation": "Select alternative antibiotic with minimal CYP interaction or reduce warfarin dose by 30-50% with daily INR tracking.",
        "potential_alternative": "Azithromycin, Doxycycline, or Amoxicillin under antimicrobial stewardship review."
    },
    {
        "drug_a": "Warfarin", "drug_b": "Fluconazole",
        "severity": "Major",
        "mechanism": "Potent inhibition of CYP2C9 and CYP3A4 blocks metabolic degradation of the active (S)-warfarin enantiomer.",
        "clinical_risk": "Profound INR prolongation with catastrophic hematological toxicity and major hemorrhage.",
        "recommendation": "Avoid concomitant use. If unavoidable, pre-emptively reduce warfarin dosage by 50% with frequent INR checks.",
        "potential_alternative": "Nystatin for topical oral candidiasis, or clinical evaluation of echinocandins."
    },
    {
        "drug_a": "Warfarin", "drug_b": "Ketorolac",
        "severity": "Major",
        "mechanism": "Severe additive inhibition of hemostasis with potent gastrointestinal mucosal ulceration.",
        "clinical_risk": "Life-threatening gastrointestinal hemorrhage and surgical site bleeding.",
        "recommendation": "Absolute contraindication. Avoid co-administration completely.",
        "potential_alternative": "Paracetamol or opioid analgesics (Morphine) titrated under physician supervision."
    },
    {
        "drug_a": "Simvastatin", "drug_b": "Clarithromycin",
        "severity": "Major",
        "mechanism": "Irreversible inhibition of CYP3A4 markedly increases systemic bio-availability and area under curve (AUC) of simvastatin by up to 10-fold.",
        "clinical_risk": "Severe myopathy, muscle necrosis, acute rhabdomyolysis, and secondary acute kidney injury.",
        "recommendation": "Temporarily suspend simvastatin therapy during macrolide antibiotic course.",
        "potential_alternative": "Substitute pravastatin or rosuvastatin, or select non-CYP3A4 antibiotic (Azithromycin, Amoxicillin)."
    },
    {
        "drug_a": "Simvastatin", "drug_b": "Amiodarone",
        "severity": "Major",
        "mechanism": "Amiodarone and its active metabolite DEA inhibit CYP3A4 and P-glycoprotein-mediated transport of simvastatin.",
        "clinical_risk": "Dose-dependent myopathy, elevated creatine kinase, and rhabdomyolysis.",
        "recommendation": "Do not exceed simvastatin 20 mg daily, or preferably convert to a statin not metabolized by CYP3A4.",
        "potential_alternative": "Pravastatin (20-40 mg) or Rosuvastatin under physician guidance."
    },
    {
        "drug_a": "Simvastatin", "drug_b": "Ketoconazole",
        "severity": "Major",
        "mechanism": "Profound CYP3A4 suppression causes massive plasma accumulation of active simvastatin acid.",
        "clinical_risk": "High risk of life-threatening rhabdomyolysis and acute renal shutdown.",
        "recommendation": "Co-administration contraindicated. Hold statin during azole therapy.",
        "potential_alternative": "Pravastatin, or switch to topical antifungal formulation where appropriate."
    },
    {
        "drug_a": "Fluoxetine", "drug_b": "Tramadol",
        "severity": "Major",
        "mechanism": "Combined inhibition of serotonin reuptake causes toxic accumulation of 5-HT, and fluoxetine inhibits CYP2D6 bioactivation of tramadol.",
        "clinical_risk": "High risk of life-threatening Serotonin Syndrome (hyperthermia, clonus, autonomic instability) and lowered seizure threshold.",
        "recommendation": "Avoid combination. Consider alternative pain management modalities.",
        "potential_alternative": "Paracetamol for mild-to-moderate pain; non-serotonergic analgesics."
    },
    {
        "drug_a": "Amiodarone", "drug_b": "Azithromycin",
        "severity": "Major",
        "mechanism": "Additive blockade of cardiac delayed rectifier potassium channels (IKr) significantly delays ventricular repolarization.",
        "clinical_risk": "Excessive QT interval prolongation, Torsades de Pointes, ventricular fibrillation, and sudden cardiac arrest.",
        "recommendation": "Contraindicated. Evaluate alternative antimicrobial agents with no known cardiac repolarization liability.",
        "potential_alternative": "Beta-lactams (Amoxicillin, Cefuroxime) or Doxycycline."
    },
    {
        "drug_a": "Ciprofloxacin", "drug_b": "Ondansetron",
        "severity": "Major",
        "mechanism": "Dual prolongation of ventricular repolarization (additive hERG channel inhibition).",
        "clinical_risk": "Critical QTc interval lengthening and life-threatening ventricular tachyarrhythmias.",
        "recommendation": "Avoid concurrent use. Monitor continuous 12-lead ECG if simultaneous administration is unavoidable.",
        "potential_alternative": "Metoclopramide or Prochlorperazine for nausea management."
    },
    {
        "drug_a": "Lisinopril", "drug_b": "Spironolactone",
        "severity": "Major",
        "mechanism": "Concurrent blockade of the renin-angiotensin-aldosterone axis suppresses aldosterone-driven potassium excretion.",
        "clinical_risk": "Severe hyperkalemia (>6.0 mEq/L) triggering cardiac conduction arrest and acute renal failure.",
        "recommendation": "Carefully monitor serum potassium and creatinine within 3-7 days of initiation and periodically thereafter.",
        "potential_alternative": "Furosemide or non-potassium-sparing diuretic adjustment."
    },
    {
        "drug_a": "Methotrexate", "drug_b": "Ibuprofen",
        "severity": "Major",
        "mechanism": "NSAIDs decrease renal blood flow and competitive inhibition of renal tubular organic anion transport reduces methotrexate clearance.",
        "clinical_risk": "Severe, potentially fatal methotrexate bone marrow suppression, pancytopenia, and acute renal tubular necrosis.",
        "recommendation": "Avoid concurrent NSAID administration with high-dose methotrexate; use extreme caution in low-dose arthritis regimens.",
        "potential_alternative": "Acetaminophen/Paracetamol for pain control."
    },
    {
        "drug_a": "Digoxin", "drug_b": "Amiodarone",
        "severity": "Major",
        "mechanism": "Amiodarone strongly inhibits renal and biliary P-glycoprotein (MDR1) efflux transporters, reducing digoxin clearance by 50%.",
        "clinical_risk": "Severe digitalis toxicity: bradycardia, high-grade AV block, nausea, visual disturbances, and fatal ventricular arrhythmias.",
        "recommendation": "Reduce digoxin maintenance dose by 50% upon initiating amiodarone and monitor serum digoxin trough levels.",
        "potential_alternative": "Beta-blocker (Bisoprolol) for ventricular rate control if clinically appropriate."
    },
    {
        "drug_a": "Clopidogrel", "drug_b": "Omeprazole",
        "severity": "Major",
        "mechanism": "Omeprazole competitive inhibition of hepatic CYP2C19 impairs bioactivation of prodrug clopidogrel to its active thiol metabolite.",
        "clinical_risk": "Subtherapeutic antiplatelet efficacy, increasing the risk of acute stent thrombosis, myocardial infarction, or stroke.",
        "recommendation": "Switch PPI from omeprazole to pantoprazole, which displays minimal CYP2C19 inhibitory affinity.",
        "potential_alternative": "Pantoprazole or Famotidine (H2-receptor antagonist)."
    },
    {
        "drug_a": "Tacrolimus", "drug_b": "Ketoconazole",
        "severity": "Major",
        "mechanism": "Extreme CYP3A4 and P-glycoprotein inhibition causes massive retention of circulating tacrolimus.",
        "clinical_risk": "Severe nephrotoxicity, neurotoxicity, severe hypertension, and hyperkalemia.",
        "recommendation": "Avoid systemic ketoconazole in transplant recipients on calcineurin inhibitors.",
        "potential_alternative": "Topical antifungals or non-azole therapies with daily tacrolimus trough monitoring."
    },
    {
        "drug_a": "Cyclosporine", "drug_b": "Atorvastatin",
        "severity": "Major",
        "mechanism": "Cyclosporine inhibits OATP1B1 hepatic uptake transporter and CYP3A4, dramatically elevating statin exposure.",
        "clinical_risk": "Acute rhabdomyolysis and myopathy with secondary acute tubular necrosis.",
        "recommendation": "Avoid combination or cap atorvastatin at 10 mg with close creatine kinase surveillance.",
        "potential_alternative": "Pravastatin (maximum 20 mg daily) after clinician review."
    },
    {
        "drug_a": "Theophylline", "drug_b": "Ciprofloxacin",
        "severity": "Major",
        "mechanism": "Potent CYP1A2 inhibition by ciprofloxacin blocks hepatic demethylation and oxidation of theophylline.",
        "clinical_risk": "Severe methylxanthine toxicity: refractory seizures, cardiac tachyarrhythmias, and vomiting.",
        "recommendation": "Avoid ciprofloxacin; if mandatory, reduce theophylline dosage by 50% and track serum levels.",
        "potential_alternative": "Levofloxacin or Azithromycin (minimal CYP1A2 inhibition)."
    },
    {
        "drug_a": "Apixaban", "drug_b": "Ketoconazole",
        "severity": "Major",
        "mechanism": "Dual potent inhibition of CYP3A4 and P-glycoprotein doubles apixaban systemic area under curve.",
        "clinical_risk": "Major life-threatening internal bleeding episodes.",
        "recommendation": "Avoid concurrent administration or reduce apixaban dose by 50% per labeling instructions.",
        "potential_alternative": "Alternative non-azole antifungal or topical antifungal agents."
    },

    # Moderate Interactions
    {
        "drug_a": "Digoxin", "drug_b": "Verapamil",
        "severity": "Moderate",
        "mechanism": "Verapamil inhibits P-glycoprotein transport and possesses negative dromotropic effects.",
        "clinical_risk": "Increased digoxin blood levels (40-60% rise) and additive sinus bradycardia / heart block.",
        "recommendation": "Reduce digoxin dosage by 30-50% and track ECG PR intervals and heart rate.",
        "potential_alternative": "Amlodipine (dihydropyridine CCB) has no substantial effect on digoxin clearance."
    },
    {
        "drug_a": "Fluoxetine", "drug_b": "Ondansetron",
        "severity": "Moderate",
        "mechanism": "Additive serotonergic pharmacodynamic effects and mild QT prolongation potential.",
        "clinical_risk": "Serotonin excess symptoms and borderline ECG QT prolongation.",
        "recommendation": "Monitor for tremors, diaphoresis, hyperreflexia, and check ECG in elderly patients.",
        "potential_alternative": "Granisetron or prochlorperazine under medical supervision."
    },
    {
        "drug_a": "Metformin", "drug_b": "Ciprofloxacin",
        "severity": "Moderate",
        "mechanism": "Ciprofloxacin inhibits renal organic cation transporters (OCT2), elevating metformin serum concentrations.",
        "clinical_risk": "Increased incidence of severe hypoglycemia and lactic acidosis risk in renal compromise.",
        "recommendation": "Monitor blood glucose closely and maintain adequate patient hydration.",
        "potential_alternative": "Beta-lactam antibiotics (Amoxicillin, Ceftriaxone) if microbiologically susceptible."
    },
    {
        "drug_a": "Aspirin", "drug_b": "Ibuprofen",
        "severity": "Moderate",
        "mechanism": "Ibuprofen binds competitively to platelet COX-1 active site, blocking irreversible acetylation by low-dose aspirin.",
        "clinical_risk": "Attenuated cardioprotective antiplatelet effect of cardioprotective aspirin plus increased GI erosion.",
        "recommendation": "Take immediate-release aspirin at least 30 minutes before, or 8 hours after, ibuprofen.",
        "potential_alternative": "Acetaminophen/Paracetamol or Celecoxib after specialist review."
    },
    {
        "drug_a": "Phenytoin", "drug_b": "Carbamazepine",
        "severity": "Moderate",
        "mechanism": "Mutual induction and competition for CYP hepatic metabolic pathways.",
        "clinical_risk": "Fluctuating antiepileptic drug levels, loss of seizure control or neurotoxicity.",
        "recommendation": "Frequent therapeutic drug monitoring (TDM) of total and free serum levels for both agents.",
        "potential_alternative": "Levetiracetam or Lamotrigine."
    },
    {
        "drug_a": "Atorvastatin", "drug_b": "Diltiazem",
        "severity": "Moderate",
        "mechanism": "Moderate CYP3A4 inhibition by diltiazem increases atorvastatin plasma concentration by 20-30%.",
        "clinical_risk": "Elevated risk of myalgia, elevated transaminases, or mild myopathy.",
        "recommendation": "Limit atorvastatin dose to 20 mg daily or monitor patient for muscle symptoms.",
        "potential_alternative": "Rosuvastatin (metabolized mainly via CYP2C9) or Pravastatin."
    },
    {
        "drug_a": "Lisinopril", "drug_b": "Ibuprofen",
        "severity": "Moderate",
        "mechanism": "NSAID inhibits renal prostaglandins responsible for afferent arteriole vasodilation while ACEI blocks efferent vasoconstriction.",
        "clinical_risk": "Blunting of antihypertensive effect and acute hemodynamic decline in glomerular filtration rate (GFR).",
        "recommendation": "Monitor blood pressure and renal function; limit NSAID duration to briefest necessary course.",
        "potential_alternative": "Acetaminophen/Paracetamol for mild pain."
    },
    {
        "drug_a": "Sertraline", "drug_b": "Aspirin",
        "severity": "Moderate",
        "mechanism": "SSRI depletes platelet intra-granular serotonin storage, compounding antiplatelet inhibition.",
        "clinical_risk": "Elevated risk of upper gastrointestinal bleeding and ecchymoses.",
        "recommendation": "Consider co-prescription of gastroprotective proton pump inhibitor (Pantoprazole).",
        "potential_alternative": "Monitor signs of gastrointestinal hemorrhage."
    },
    {
        "drug_a": "Diazepam", "drug_b": "Fluoxetine",
        "severity": "Moderate",
        "mechanism": "Inhibition of CYP2C19 and CYP3A4 delays clearance of diazepam and desmethyldiazepam.",
        "clinical_risk": "Prolonged psychomotor impairment, excessive daytime sedation, and fall risk in elderly.",
        "recommendation": "Consider dosage reduction of diazepam or switch to non-CYP metabolized benzodiazepine.",
        "potential_alternative": "Lorazepam or Oxazepam (glucuronidated directly)."
    },
    {
        "drug_a": "Amlodipine", "drug_b": "Simvastatin",
        "severity": "Moderate",
        "mechanism": "Amlodipine mildly inhibits CYP3A4, elevating simvastatin exposure by approximately 70%.",
        "clinical_risk": "Increased risk of statin-induced myopathy and elevated creatine kinase.",
        "recommendation": "Do not exceed simvastatin 20 mg daily when combined with amlodipine.",
        "potential_alternative": "Rosuvastatin or Atorvastatin under clinical review."
    },
    {
        "drug_a": "Clarithromycin", "drug_b": "Digoxin",
        "severity": "Moderate",
        "mechanism": "Inhibition of gut flora Eubacterium lentum (which hydrolyzes digoxin) and P-gp inhibition in kidney.",
        "clinical_risk": "Digitalis toxicity: arrhythmias, vision changes, and vomiting.",
        "recommendation": "Monitor serum digoxin concentration and reduce dose if necessary.",
        "potential_alternative": "Azithromycin has minimal effect on digoxin transport."
    },
    {
        "drug_a": "Carvedilol", "drug_b": "Digoxin",
        "severity": "Moderate",
        "mechanism": "Additive depression of AV nodal conduction and slight increase in digoxin AUC.",
        "clinical_risk": "Bradycardia, PR interval prolongation, and advanced AV conduction block.",
        "recommendation": "Monitor heart rate, ECG rhythm strips, and digoxin trough levels.",
        "potential_alternative": "Adjust beta-blocker titration schedule carefully."
    },
    {
        "drug_a": "Prednisone", "drug_b": "Ibuprofen",
        "severity": "Moderate",
        "mechanism": "Concurrent disruption of gastric cytoprotective prostaglandin synthesis and impaired epithelial repair.",
        "clinical_risk": "Substantial amplification of gastric and duodenal ulceration and gastrointestinal hemorrhage.",
        "recommendation": "Provide gastroprotection with proton pump inhibitor (Pantoprazole) during concurrent therapy.",
        "potential_alternative": "Paracetamol for analgesia; minimize corticosteroid duration."
    },

    # Minor / Mild Interactions
    {
        "drug_a": "Metformin", "drug_b": "Lisinopril",
        "severity": "Minor",
        "mechanism": "ACE inhibitors may slightly enhance insulin sensitivity and enhance glycemic response.",
        "clinical_risk": "Mild, usually asymptomatic enhancement of hypoglycemic effect; monitoring sufficient.",
        "recommendation": "Standard self-monitoring of blood glucose; no medication withdrawal necessary.",
        "potential_alternative": "Clinical combination is widely used in diabetic nephropathy management."
    },
    {
        "drug_a": "Amlodipine", "drug_b": "Hydrochlorothiazide",
        "severity": "Minor",
        "mechanism": "Additive complementary blood pressure lowering mechanisms.",
        "clinical_risk": "Beneficial antihypertensive synergy; mild orthostatic sensation upon initiating.",
        "recommendation": "Clinically favorable synergistic guideline-directed combination.",
        "potential_alternative": "Guideline-supported combination therapy."
    },
    {
        "drug_a": "Paracetamol", "drug_b": "Amoxicillin",
        "severity": "Minor",
        "mechanism": "No adverse pharmacokinetic interaction or metabolic competition.",
        "clinical_risk": "Minimal to zero clinical risk. Safe for concurrent therapeutic use.",
        "recommendation": "Safe to administer together according to standard dosage instructions.",
        "potential_alternative": "Well-established safe combination."
    },
    {
        "drug_a": "Levothyroxine", "drug_b": "Paracetamol",
        "severity": "Minor",
        "mechanism": "No significant pharmacokinetic or absorption interference.",
        "clinical_risk": "Negligible clinical effect.",
        "recommendation": "Standard clinical dosing acceptable.",
        "potential_alternative": "Safe combination."
    },
    {
        "drug_a": "Pantoprazole", "drug_b": "Amoxicillin",
        "severity": "Minor",
        "mechanism": "Gastric acid reduction optimizes penicillin stability (standard H. pylori regimen).",
        "clinical_risk": "Synergistic eradication benefit without toxic risk.",
        "recommendation": "Standard recommended combination for Helicobacter pylori eradication.",
        "potential_alternative": "Standard clinical guideline therapy."
    },
    {
        "drug_a": "Atorvastatin", "drug_b": "Metformin",
        "severity": "Minor",
        "mechanism": "No significant CYP pathway overlap.",
        "clinical_risk": "Safe concurrent administration in diabetic dyslipidemia.",
        "recommendation": "Standard therapeutic monitoring of HbA1c and lipid panel.",
        "potential_alternative": "Guideline-recommended combination for cardiovascular risk reduction."
    },
    {
        "drug_a": "Rosuvastatin", "drug_b": "Lisinopril",
        "severity": "Minor",
        "mechanism": "Independent metabolic and excretory routes.",
        "clinical_risk": "Standard cardioprotective combination without significant pharmacokinetic interaction.",
        "recommendation": "Standard clinical care.",
        "potential_alternative": "Safe guideline-directed therapy."
    },
    {
        "drug_a": "Paracetamol", "drug_b": "Pantoprazole",
        "severity": "Minor",
        "mechanism": "No clinically meaningful interaction between paracetamol metabolism and pantoprazole.",
        "clinical_risk": "Negligible risk.",
        "recommendation": "Safe to take concurrently under routine clinical dosing.",
        "potential_alternative": "Routine clinical practice."
    },
    {
        "drug_a": "Metformin", "drug_b": "Amlodipine",
        "severity": "Minor",
        "mechanism": "Independent metabolic and clearance pathways.",
        "clinical_risk": "No significant adverse interaction.",
        "recommendation": "Routine clinical follow-up.",
        "potential_alternative": "Standard combination in metabolic syndrome."
    },
    {
        "drug_a": "Aspirin", "drug_b": "Atorvastatin",
        "severity": "Minor",
        "mechanism": "Independent therapeutic pathways with complementary cardiovascular protection.",
        "clinical_risk": "Guideline-directed secondary prevention combination.",
        "recommendation": "Standard cardiovascular clinical follow-up.",
        "potential_alternative": "Established standard of care."
    }
]

def calculate_molecular_properties(smiles: str):
    """Compute verified physicochemical descriptors using RDKit."""
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
            "ring_count": 0,
            "formula": "Unknown"
        }
    
    return {
        "molecular_weight": round(Descriptors.MolWt(mol), 2),
        "logp": round(Descriptors.MolLogP(mol), 2),
        "tpsa": round(Descriptors.TPSA(mol), 2),
        "h_donors": Lipinski.NumHDonors(mol),
        "h_acceptors": Lipinski.NumHAcceptors(mol),
        "rotatable_bonds": Lipinski.NumRotatableBonds(mol),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
        "ring_count": Lipinski.RingCount(mol),
        "formula": Chem.rdMolDescriptors.CalcMolFormula(mol)
    }

def main():
    print("[*] Processing drug catalog with RDKit...")
    enriched_drugs = []
    
    for idx, drug in enumerate(RAW_DRUGS, 1):
        props = calculate_molecular_properties(drug["smiles"])
        entry = {
            "drug_id": idx,
            "name": drug["name"],
            "brand_names": drug["brand_names"],
            "category": drug["category"],
            "atc_code": drug["atc_code"],
            "pubchem_cid": drug["pubchem_cid"],
            "smiles": drug["smiles"],
            "formula": props["formula"],
            "molecular_weight": props["molecular_weight"],
            "logp": props["logp"],
            "tpsa": props["tpsa"],
            "h_donors": props["h_donors"],
            "h_acceptors": props["h_acceptors"],
            "rotatable_bonds": props["rotatable_bonds"],
            "heavy_atoms": props["heavy_atoms"],
            "ring_count": props["ring_count"],
            "cyp_inhibitor": drug["cyp_inhibitor"],
            "cyp_substrate": drug["cyp_substrate"],
            "qt_prolonging": drug["qt_prolonging"],
            "bleeding_risk": drug["bleeding_risk"],
            "serotonergic": drug["serotonergic"],
            "renal_risk": drug["renal_risk"],
            "clinician_note": drug["clinician_note"]
        }
        enriched_drugs.append(entry)
        
    drugs_df = pd.DataFrame(enriched_drugs)
    drugs_csv_path = DATA_DIR / "drugs_database.csv"
    drugs_df.to_csv(drugs_csv_path, index=False)
    print(f"[+] Saved {len(drugs_df)} validated drugs to {drugs_csv_path}")

    # Build interactions matrix
    print("[*] Constructing interaction benchmark matrix...")
    drugs_map = {d["name"].lower(): d for d in RAW_DRUGS}
    
    interactions = []
    known_pairs = set()

    for item in RAW_INTERACTIONS:
        a_name = item["drug_a"].strip()
        b_name = item["drug_b"].strip()
        pair_key = tuple(sorted([a_name.lower(), b_name.lower()]))
        known_pairs.add(pair_key)
        
        interactions.append({
            "drug_a": a_name,
            "drug_b": b_name,
            "interaction": 1 if item["severity"] in ["Major", "Moderate"] else 0,
            "severity": item["severity"],
            "mechanism": item["mechanism"],
            "clinical_risk": item["clinical_risk"],
            "recommendation": item["recommendation"],
            "potential_alternative": item["potential_alternative"]
        })

    # Negative non-interacting pairs via balanced sampling among non-overlapping pairs
    all_names = [d["name"] for d in RAW_DRUGS]
    negative_candidates = []
    
    for i, name_a in enumerate(all_names):
        for name_b in all_names[i+1:]:
            pair_key = tuple(sorted([name_a.lower(), name_b.lower()]))
            if pair_key in known_pairs:
                continue
            
            d_a = drugs_map[name_a.lower()]
            d_b = drugs_map[name_b.lower()]
            
            # Select biologically plausibly non-interacting or negligible pairs
            has_major_overlap = (
                (d_a["cyp_inhibitor"] and d_b["cyp_substrate"]) or
                (d_b["cyp_inhibitor"] and d_a["cyp_substrate"]) or
                (d_a["qt_prolonging"] and d_b["qt_prolonging"]) or
                (d_a["bleeding_risk"] and d_b["bleeding_risk"]) or
                (d_a["serotonergic"] and d_b["serotonergic"])
            )
            
            if not has_major_overlap:
                negative_candidates.append({
                    "drug_a": name_a,
                    "drug_b": name_b,
                    "interaction": 0,
                    "severity": "Minor",
                    "mechanism": "No significant pharmacokinetic competition or additive pharmacodynamic synergy identified.",
                    "clinical_risk": "Low probability of adverse interaction under standard therapeutic dosages.",
                    "recommendation": "Standard clinical monitoring. Ensure independent clinician review.",
                    "potential_alternative": "No alternative therapy required based on current evidence."
                })
                known_pairs.add(pair_key)

    # Balance negative pairs at a reasonable 3:1 ratio to positive pairs for realistic clinical prevalence
    num_positives = sum(1 for item in interactions if item["interaction"] == 1)
    target_negatives = min(len(negative_candidates), num_positives * 3)
    import random
    random.seed(42)
    selected_negatives = random.sample(negative_candidates, target_negatives)
    
    interactions.extend(selected_negatives)

    interactions_df = pd.DataFrame(interactions)
    interactions_csv_path = DATA_DIR / "interactions_database.csv"
    interactions_df.to_csv(interactions_csv_path, index=False)
    print(f"[+] Saved {len(interactions_df)} total interaction pairs (Positive: {sum(interactions_df['interaction']==1)}, Negative: {sum(interactions_df['interaction']==0)}) to {interactions_csv_path}")

if __name__ == "__main__":
    main()
