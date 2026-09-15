import json
from typing import Dict, Any, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.app.models.drug import Drug
from backend.app.models.interaction import DrugInteraction
from backend.app.models.alert import Alert
from backend.app.schemas.interaction_schema import InteractionRequest, InteractionResponse, ShapFeatureContribution
from backend.app.ml.predictor import predictor
from backend.app.ml.explainer import explainer_service
from backend.app.utils.logger import logger

class InteractionService:
    @staticmethod
    def _create_plain_explanation(features: Dict[str, float]) -> List[str]:
        reasons = []
        if features.get("both_bleeding_risk", 0) == 1:
            reasons.append("Additive Hemostatic Risk: Both medications independently impair platelet activation or coagulation cascade.")
        if features.get("cyp_inhibitor_substrate_pair", 0) == 1:
            reasons.append("CYP Metabolic Competition: One agent inhibits hepatic cytochrome P450 enzymes responsible for clearing the co-administered drug.")
        if features.get("both_qt_prolonging", 0) == 1:
            reasons.append("Cardiac Repolarization Risk: Concomitant administration compounds myocardial potassium channel blockade, elevating ventricular arrhythmia risk.")
        if features.get("both_serotonergic", 0) == 1:
            reasons.append("Central Serotonergic Synergism: Both compounds elevate synaptic serotonin concentrations, creating potential for Serotonin Toxicity.")
        if features.get("both_renal_risk", 0) == 1:
            reasons.append("Hemodynamic / Nephrotoxic Strain: Both agents alter renal glomerular filtration pressure or tubular clearance.")
        if features.get("same_category", 0) == 1:
            reasons.append("Therapeutic Redundancy: Both drugs share the same pharmacological class, increasing likelihood of cumulative receptor saturation.")
        if features.get("tanimoto_similarity", 0.0) > 0.35:
            reasons.append(f"Structural Chemical Congruence: Elevated ECFP4 fingerprint similarity ({features['tanimoto_similarity']:.2f}) suggests potential shared target binding.")

        if not reasons:
            reasons.append("Low molecular and pharmacological cross-reactivity detected under standard predictive thresholds.")

        return reasons

    @staticmethod
    def check_interaction(db: Session, request: InteractionRequest) -> InteractionResponse:
        name_a = request.drug_a.strip()
        name_b = request.drug_b.strip()

        # Validation 1: Empty input
        if not name_a or not name_b:
            raise HTTPException(status_code=400, detail="Both Drug A and Drug B must be specified.")

        # Validation 2: Same drug selected twice
        if name_a.lower() == name_b.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate medication selected: '{name_a}'. Please select two distinct drugs to evaluate interaction risk."
            )

        # Retrieve drugs from database
        drug_a = db.query(Drug).filter(Drug.name.ilike(name_a)).first()
        drug_b = db.query(Drug).filter(Drug.name.ilike(name_b)).first()

        # Validation 3: Unknown drug
        if drug_a is None or drug_b is None:
            missing = name_a if drug_a is None else name_b
            raise HTTPException(
                status_code=404,
                detail=f"Drug '{missing}' is not cataloged in the clinical reference database."
            )

        drug_a_dict = {c.name: getattr(drug_a, c.name) for c in drug_a.__table__.columns}
        drug_b_dict = {c.name: getattr(drug_b, c.name) for c in drug_b.__table__.columns}

        # Check known clinical interactions table
        known_inter = db.query(DrugInteraction).filter(
            or_(
                and_(DrugInteraction.drug_a.ilike(name_a), DrugInteraction.drug_b.ilike(name_b)),
                and_(DrugInteraction.drug_a.ilike(name_b), DrugInteraction.drug_b.ilike(name_a))
            )
        ).first()

        # Compute ML prediction & feature vector
        ml_prob, features, is_ml = predictor.predict_pair(drug_a_dict, drug_b_dict)

        # Compute SHAP feature attributions
        shap_contributions = explainer_service.explain_instance(features, top_k=5)
        plain_reasons = InteractionService._create_plain_explanation(features)

        if known_inter is not None:
            severity = known_inter.severity.capitalize()
            source = "Verified Clinical Benchmark Database"
            mechanism = known_inter.mechanism
            clinical_effect = known_inter.clinical_risk
            recommendation = known_inter.recommendation
            
            # Calibrate probability based on established severity
            if severity == "Major":
                calibrated_prob = max(ml_prob, 0.88)
            elif severity == "Moderate":
                calibrated_prob = max(ml_prob, 0.62)
            else:
                calibrated_prob = min(ml_prob, 0.35)
                
            risk_probability = round(calibrated_prob, 3)
            detected = severity in ["Major", "Moderate"]
            alternative = known_inter.potential_alternative
        else:
            source = f"Machine Learning ({predictor.model_name} + RDKit ECFP4)"
            risk_probability = round(ml_prob, 3)
            detected = risk_probability >= 0.40
            
            if risk_probability >= 0.70:
                severity = "Major"
                clinical_effect = "High predictive probability of adverse drug interaction. Close clinician review warranted."
                recommendation = "Evaluate alternative non-interacting pharmacotherapy or adjust dosage with clinical monitoring."
            elif risk_probability >= 0.40:
                severity = "Moderate"
                clinical_effect = "Moderate interaction potential identified through molecular and metabolic feature overlap."
                recommendation = "Standard clinical vigilance; monitor patient symptoms and relevant laboratory markers."
            else:
                severity = "Minor"
                clinical_effect = "Low interaction probability predicted by the model under therapeutic dosage."
                recommendation = "Standard clinical care. Confirm indications and patient-specific contraindications."

            mechanism = "Predicted via multi-feature molecular descriptors, Tanimoto fingerprint similarity, and metabolic pathways."
            
            # Compile alternative suggestion only if reliable clinician note exists
            alt_parts = []
            if drug_a.clinician_note:
                alt_parts.append(f"For {drug_a.name}: {drug_a.clinician_note}")
            if drug_b.clinician_note:
                alt_parts.append(f"For {drug_b.name}: {drug_b.clinician_note}")
                
            alternative = " ".join(alt_parts) if alt_parts else "No verified alternative information is available in the current formulary."

        # Ensure disclaimer is included if alternatives are suggested
        if alternative and "No verified" not in alternative:
            alternative += " (Note: Clinical evaluation of patient kidney/liver status and allergies is strictly required)."

        # Save alert record to database
        try:
            alert = Alert(
                drug_a=drug_a.name,
                drug_b=drug_b.name,
                interaction_detected=1 if detected else 0,
                risk_probability=risk_probability,
                severity=severity,
                source=source,
                mechanism=mechanism,
                clinical_effect=clinical_effect,
                recommendation=recommendation,
                safer_alternative=alternative,
                explanation=json.dumps(plain_reasons),
                shap_features=json.dumps([s.model_dump() for s in shap_contributions])
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
        except Exception as e:
            db.rollback()
            logger.error(f"Could not persist alert to database: {e}")

        return InteractionResponse(
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

interaction_service = InteractionService()
