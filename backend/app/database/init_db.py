from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.database.connection import engine, Base, SessionLocal
from backend.app.models.drug import Drug
from backend.app.models.interaction import DrugInteraction
from backend.app.utils.config import settings
from backend.app.utils.logger import logger

def init_db(db: Session = None):
    """Create all database tables and seed verified drugs if empty."""
    Base.metadata.create_all(bind=engine)
    
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        drug_count = db.query(Drug).count()
        if drug_count == 0 and settings.DRUGS_DATA_PATH.exists():
            logger.info(f"Seeding drug database from {settings.DRUGS_DATA_PATH}...")
            df_drugs = pd.read_csv(settings.DRUGS_DATA_PATH)
            for _, row in df_drugs.iterrows():
                drug = Drug(
                    name=str(row["name"]).strip(),
                    brand_names=str(row.get("brand_names", "")),
                    category=str(row.get("category", "")),
                    atc_code=str(row.get("atc_code", "")),
                    pubchem_cid=int(row["pubchem_cid"]) if pd.notna(row.get("pubchem_cid")) else None,
                    smiles=str(row.get("smiles", "")),
                    formula=str(row.get("formula", "")),
                    molecular_weight=float(row.get("molecular_weight", 0.0)),
                    logp=float(row.get("logp", 0.0)),
                    tpsa=float(row.get("tpsa", 0.0)),
                    h_donors=int(row.get("h_donors", 0)),
                    h_acceptors=int(row.get("h_acceptors", 0)),
                    rotatable_bonds=int(row.get("rotatable_bonds", 0)),
                    heavy_atoms=int(row.get("heavy_atoms", 0)),
                    ring_count=int(row.get("ring_count", 0)),
                    cyp_inhibitor=int(row.get("cyp_inhibitor", 0)),
                    cyp_substrate=int(row.get("cyp_substrate", 0)),
                    qt_prolonging=int(row.get("qt_prolonging", 0)),
                    bleeding_risk=int(row.get("bleeding_risk", 0)),
                    serotonergic=int(row.get("serotonergic", 0)),
                    renal_risk=int(row.get("renal_risk", 0)),
                    clinician_note=str(row.get("clinician_note", "")) if pd.notna(row.get("clinician_note")) else None
                )
                db.add(drug)
            db.commit()
            logger.info(f"Seeded {len(df_drugs)} verified drug compounds.")

        interaction_count = db.query(DrugInteraction).count()
        if interaction_count == 0 and settings.INTERACTIONS_DATA_PATH.exists():
            logger.info(f"Seeding interaction reference matrix from {settings.INTERACTIONS_DATA_PATH}...")
            df_inter = pd.read_csv(settings.INTERACTIONS_DATA_PATH)
            for _, row in df_inter.iterrows():
                if int(row.get("interaction", 0)) == 1: # Only seed known active interactions into reference table
                    inter = DrugInteraction(
                        drug_a=str(row["drug_a"]).strip(),
                        drug_b=str(row["drug_b"]).strip(),
                        severity=str(row.get("severity", "Moderate")),
                        mechanism=str(row.get("mechanism", "")),
                        clinical_risk=str(row.get("clinical_risk", "")),
                        recommendation=str(row.get("recommendation", "")),
                        potential_alternative=str(row.get("potential_alternative", "")) if pd.notna(row.get("potential_alternative")) else None
                    )
                    db.add(inter)
            db.commit()
            logger.info("Seeded clinical drug-drug interaction reference records.")

        # Seed synthetic demonstration patients if empty
        from backend.app.models.patient import Patient
        from backend.app.models.patient_medication import PatientMedication
        patient_count = db.query(Patient).count()
        if patient_count == 0:
            logger.info("Seeding synthetic demonstration patient profiles...")
            p1 = Patient(
                patient_id="DEMO-PT-1001",
                name="Demo Patient (Cardiovascular & Endocrine)",
                age=68,
                sex="Male",
                conditions="Atrial Fibrillation, Hypertension, Type 2 Diabetes Mellitus",
                allergies="Penicillin V, Amoxicillin (Severe Rash)",
                medical_history="Diagnosed with T2DM in 2014; AFib diagnosed in 2020. Mild chronic renal impairment (eGFR 55 mL/min).",
                surgeries="Coronary stent placement (LAD, 2021)"
            )
            db.add(p1)
            db.flush()

            meds_p1 = [
                PatientMedication(patient_id=p1.id, drug_name="Warfarin", dose="5 mg", frequency="Once daily in evening", route="Oral", status="Current", source="Manual", notes="Target INR 2.0 - 3.0"),
                PatientMedication(patient_id=p1.id, drug_name="Metformin", dose="500 mg", frequency="Twice daily with meals", route="Oral", status="Current", source="Manual", notes="Glycemic control"),
                PatientMedication(patient_id=p1.id, drug_name="Amlodipine", dose="5 mg", frequency="Once daily in morning", route="Oral", status="Current", source="Manual", notes="Blood pressure control"),
                PatientMedication(patient_id=p1.id, drug_name="Aspirin", dose="75 mg", frequency="Once daily", route="Oral", status="Previous", source="Manual", notes="Discontinued due to mild hematoma")
            ]
            for m in meds_p1:
                db.add(m)

            p2 = Patient(
                patient_id="DEMO-PT-1002",
                name="Demo Patient (Psychiatry & Gastroenterology)",
                age=42,
                sex="Female",
                conditions="Major Depressive Disorder, Gastroesophageal Reflux Disease (GERD)",
                allergies="Sulfa antibiotics (Urticaria)",
                medical_history="Recurrent depressive episodes; persistent acid reflux managed with PPI therapy.",
                surgeries="Laparoscopic cholecystectomy (2018)"
            )
            db.add(p2)
            db.flush()

            meds_p2 = [
                PatientMedication(patient_id=p2.id, drug_name="Fluoxetine", dose="20 mg", frequency="Once daily in morning", route="Oral", status="Current", source="Manual", notes="SSRI for depression"),
                PatientMedication(patient_id=p2.id, drug_name="Omeprazole", dose="20 mg", frequency="Once daily before breakfast", route="Oral", status="Current", source="Manual", notes="PPI for acid reflux")
            ]
            for m in meds_p2:
                db.add(m)

            db.commit()
            logger.info("Seeded 2 synthetic demonstration patient profiles.")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to initialize and seed database: {e}")
    finally:
        if close_after:
            db.close()

if __name__ == "__main__":
    init_db()
