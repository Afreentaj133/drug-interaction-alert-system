import itertools
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.app.models.patient import Patient
from backend.app.models.patient_medication import PatientMedication
from backend.app.models.drug import Drug
from backend.app.models.interaction import DrugInteraction
from backend.app.models.alert import Alert
from backend.app.ml.predictor import predictor
from backend.app.ml.explainer import explainer_service
from backend.app.schemas.patient_schema import PolypharmacyPairResult, PolypharmacyScreeningResponse
from backend.app.schemas.interaction_schema import ShapFeatureContribution
from backend.app.services.interaction_service import InteractionService
from backend.app.utils.logger import logger

class PolypharmacyService:
    @staticmethod
    def screen_patient_medications(db: Session, patient: Patient) -> PolypharmacyScreeningResponse:
        """
        Extracts active current medications for a patient, generates all unique pairs N*(N-1)/2,
        and screens each pair using the authentic ML and benchmark interaction pipeline.
        """
        # 1. Fetch current active medications
        active_meds = [m for m in patient.medications if m.status == "Current"]
        drug_names = list(dict.fromkeys([m.drug_name.strip() for m in active_meds if m.drug_name]))

        major_pairs: List[PolypharmacyPairResult] = []
        moderate_pairs: List[PolypharmacyPairResult] = []
        minor_pairs: List[PolypharmacyPairResult] = []
        unsupported_pairs: List[PolypharmacyPairResult] = []

        # Track cumulative mechanism flags across the patient's entire regimen
        qt_prolonging_drugs = []
        bleeding_risk_drugs = []
        cyp_inhibitors = []
        cyp_substrates = []
        serotonergic_drugs = []
        renal_risk_drugs = []

        # Load all drug records for active medications
        drug_records: Dict[str, Drug] = {}
        for name in drug_names:
            drug = db.query(Drug).filter(Drug.name.ilike(name)).first()
            if drug:
                drug_records[name.lower()] = drug
                if drug.qt_prolonging:
                    qt_prolonging_drugs.append(drug.name)
                if drug.bleeding_risk:
                    bleeding_risk_drugs.append(drug.name)
                if drug.cyp_inhibitor:
                    cyp_inhibitors.append(drug.name)
                if drug.cyp_substrate:
                    cyp_substrates.append(drug.name)
                if drug.serotonergic:
                    serotonergic_drugs.append(drug.name)
                if drug.renal_risk:
                    renal_risk_drugs.append(drug.name)

        # 2. Generate unique combination pairs N*(N-1)/2
        pairs = list(itertools.combinations(drug_names, 2))

        for name_a, name_b in pairs:
            drug_a = drug_records.get(name_a.lower())
            drug_b = drug_records.get(name_b.lower())

            # If either drug is not cataloged or lacks molecular features
            if not drug_a or not drug_b:
                unsupported_pairs.append(
                    PolypharmacyPairResult(
                        drug_a=name_a,
                        drug_b=name_b,
                        interaction_detected=False,
                        risk_probability=0.0,
                        severity="Unsupported",
                        source="Insufficient Data",
                        mechanism="Missing chemical structure or formulary profile for one or both compounds.",
                        clinical_effect="Insufficient model/data support for this combination. Please consult clinical formularies directly.",
                        recommendation="Independent clinical pharmacological review required.",
                        safer_alternative=None,
                        explanation=["Chemical descriptors or SMILES unavailable in catalog."],
                        shap_contributions=[]
                    )
                )
                continue

            drug_a_dict = {c.name: getattr(drug_a, c.name) for c in drug_a.__table__.columns}
            drug_b_dict = {c.name: getattr(drug_b, c.name) for c in drug_b.__table__.columns}

            # Check known clinical interactions table first
            known_inter = db.query(DrugInteraction).filter(
                or_(
                    and_(DrugInteraction.drug_a.ilike(name_a), DrugInteraction.drug_b.ilike(name_b)),
                    and_(DrugInteraction.drug_a.ilike(name_b), DrugInteraction.drug_b.ilike(name_a))
                )
            ).first()

            # Run ML prediction & XAI
            ml_prob, features, is_ml = predictor.predict_pair(drug_a_dict, drug_b_dict)
            shap_contributions = explainer_service.explain_instance(features, top_k=4)
            plain_reasons = InteractionService._create_plain_explanation(features)

            if known_inter is not None:
                severity = known_inter.severity.capitalize()
                source = "Verified Clinical Benchmark"
                mechanism = known_inter.mechanism
                clinical_effect = known_inter.clinical_risk
                recommendation = known_inter.recommendation
                calibrated_prob = max(ml_prob, 0.88) if severity == "Major" else (max(ml_prob, 0.62) if severity == "Moderate" else min(ml_prob, 0.35))
                risk_probability = round(calibrated_prob, 3)
                detected = severity in ["Major", "Moderate"]
                alternative = known_inter.potential_alternative
            else:
                source = f"Machine Learning ({predictor.model_name} + RDKit ECFP4)"
                risk_probability = round(ml_prob, 3)
                detected = risk_probability >= 0.40
                if risk_probability >= 0.70:
                    severity = "Major"
                    clinical_effect = "High predictive risk of severe adverse drug interaction."
                    recommendation = "Review alternative non-interacting therapies or implement therapeutic drug monitoring."
                elif risk_probability >= 0.40:
                    severity = "Moderate"
                    clinical_effect = "Moderate interaction potential identified through molecular and metabolic feature overlap."
                    recommendation = "Maintain clinical vigilance and monitor pertinent laboratory indices."
                else:
                    severity = "Minor"
                    clinical_effect = "Low interaction probability predicted under standard therapeutic dosing."
                    recommendation = "Standard supportive care and baseline monitoring."

                mechanism = "Calculated via RDKit molecular descriptors, Morgan fingerprints, and pharmacological flags."
                alternative = "Review formulary for non-interacting therapeutic alternatives."

            pair_result = PolypharmacyPairResult(
                drug_a=drug_a.name,
                drug_b=drug_b.name,
                interaction_detected=detected,
                risk_probability=risk_probability,
                severity=severity,
                source=source,
                mechanism=mechanism,
                clinical_effect=clinical_effect,
                recommendation=recommendation,
                safer_alternative=alternative,
                explanation=plain_reasons,
                shap_contributions=shap_contributions
            )

            if severity == "Major":
                major_pairs.append(pair_result)
            elif severity == "Moderate":
                moderate_pairs.append(pair_result)
            else:
                minor_pairs.append(pair_result)

        # 3. Generate cumulative mechanism warnings
        mechanism_warnings = []
        if len(bleeding_risk_drugs) >= 2:
            mechanism_warnings.append(
                f"Additive Hemostatic Hazard: Patient is concurrently prescribed {len(bleeding_risk_drugs)} medications with bleeding propensity ({', '.join(bleeding_risk_drugs)})."
            )
        if len(qt_prolonging_drugs) >= 2:
            mechanism_warnings.append(
                f"Cumulative Arrhythmia Risk: Concurrent administration of {len(qt_prolonging_drugs)} QT-prolonging agents ({', '.join(qt_prolonging_drugs)}) compounds ventricular repolarization delay."
            )
        if cyp_inhibitors and cyp_substrates:
            mechanism_warnings.append(
                f"Hepatic CYP Competition: Co-prescription of metabolic inhibitors ({', '.join(set(cyp_inhibitors))}) and substrates ({', '.join(set(cyp_substrates))}) may cause elevated plasma concentrations and drug toxicity."
            )
        if len(serotonergic_drugs) >= 2:
            mechanism_warnings.append(
                f"Serotonin Overload Warning: Multiple serotonergic agents ({', '.join(serotonergic_drugs)}) pose risk for Serotonin Syndrome."
            )
        if len(renal_risk_drugs) >= 2:
            mechanism_warnings.append(
                f"Nephrotoxic Burden: Combined regimen includes {len(renal_risk_drugs)} agents with renal clearance impact ({', '.join(renal_risk_drugs)})."
            )

        return PolypharmacyScreeningResponse(
            patient_id=patient.patient_id,
            patient_name=patient.name,
            total_medications=len(drug_names),
            total_pairs_screened=len(pairs),
            major_risk_count=len(major_pairs),
            moderate_risk_count=len(moderate_pairs),
            minor_risk_count=len(minor_pairs),
            unsupported_count=len(unsupported_pairs),
            major_pairs=major_pairs,
            moderate_pairs=moderate_pairs,
            minor_pairs=minor_pairs,
            unsupported_pairs=unsupported_pairs,
            mechanism_warnings=mechanism_warnings,
            disclaimer=(
                "Clinical Decision-Support Prototype. All interaction alerts and cumulative risk signals must be "
                "reviewed and validated by a licensed physician or clinical pharmacist prior to therapeutic decisions."
            )
        )

polypharmacy_service = PolypharmacyService()
