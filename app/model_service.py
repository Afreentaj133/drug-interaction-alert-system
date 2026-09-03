from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = BASE_DIR / "models" / "ddi_model.joblib"

drugs_df = pd.read_csv(DATA_DIR / "drugs.csv")
interactions_df = pd.read_csv(DATA_DIR / "interactions.csv")
artifact = joblib.load(MODEL_PATH)

model = artifact["model"]
feature_columns = artifact["feature_columns"]

drugs_lookup = {
    row["drug_name"].strip().lower(): row
    for _, row in drugs_df.iterrows()
}

def normalize_drug_name(name: str) -> str:
    return name.strip().lower()

def get_drug_names():
    return sorted(drugs_df["drug_name"].tolist())

def get_drug(name: str):
    return drugs_lookup.get(normalize_drug_name(name))

def find_known_interaction(drug_a: str, drug_b: str):
    a = normalize_drug_name(drug_a)
    b = normalize_drug_name(drug_b)

    for _, row in interactions_df.iterrows():
        row_a = normalize_drug_name(row["drug_a"])
        row_b = normalize_drug_name(row["drug_b"])

        if {a, b} == {row_a, row_b}:
            return row

    return None

def create_pair_features(drug_a, drug_b):
    return {
        "same_class": int(drug_a["drug_class"] == drug_b["drug_class"]),
        "both_cyp3a4_related": int(
            drug_a["cyp3a4_substrate"] and drug_b["cyp3a4_substrate"]
        ),
        "cyp_inhibitor_substrate_pair": int(
            (drug_a["cyp3a4_inhibitor"] and drug_b["cyp3a4_substrate"])
            or (drug_b["cyp3a4_inhibitor"] and drug_a["cyp3a4_substrate"])
        ),
        "both_qt_prolonging": int(
            drug_a["qt_prolonging"] and drug_b["qt_prolonging"]
        ),
        "both_bleeding_risk": int(
            drug_a["bleeding_risk"] and drug_b["bleeding_risk"]
        ),
        "both_serotonergic": int(
            drug_a["serotonergic"] and drug_b["serotonergic"]
        ),
        "both_renal_risk": int(
            drug_a["renal_risk"] and drug_b["renal_risk"]
        ),
        "drug_a_cyp_inhibitor": int(drug_a["cyp3a4_inhibitor"]),
        "drug_b_cyp_inhibitor": int(drug_b["cyp3a4_inhibitor"]),
        "drug_a_qt": int(drug_a["qt_prolonging"]),
        "drug_b_qt": int(drug_b["qt_prolonging"]),
    }

def create_explanation(features):
    labels = {
        "same_class": "Both medicines belong to the same therapeutic class.",
        "both_cyp3a4_related": "Both medicines are associated with CYP3A4 metabolism.",
        "cyp_inhibitor_substrate_pair": "One medicine may inhibit CYP3A4 metabolism of the other.",
        "both_qt_prolonging": "Both medicines have QT-prolongation risk features.",
        "both_bleeding_risk": "Both medicines have bleeding-risk features.",
        "both_serotonergic": "Both medicines have serotonergic activity features.",
        "both_renal_risk": "Both medicines have renal-risk features.",
    }

    active_reasons = [
        labels[key]
        for key, value in features.items()
        if value == 1 and key in labels
    ]

    if not active_reasons:
        active_reasons.append(
            "No high-risk rule-based feature combination was identified in the prototype dataset."
        )

    return active_reasons[:4]

def probability_to_severity(probability: float) -> str:
    if probability >= 0.75:
        return "Major"
    if probability >= 0.45:
        return "Moderate"
    return "Minor"

def predict_interaction(drug_a_name: str, drug_b_name: str):
    drug_a = get_drug(drug_a_name)
    drug_b = get_drug(drug_b_name)

    if drug_a is None or drug_b is None:
        missing = drug_a_name if drug_a is None else drug_b_name
        raise ValueError(
            f"'{missing}' is not available in the prototype drug database."
        )

    if normalize_drug_name(drug_a_name) == normalize_drug_name(drug_b_name):
        raise ValueError("Please select two different drugs.")

    known = find_known_interaction(drug_a_name, drug_b_name)
    features = create_pair_features(drug_a, drug_b)
    feature_frame = pd.DataFrame([features])[feature_columns]
    probability = float(model.predict_proba(feature_frame)[0][1])

    if known is not None:
        severity = str(known["severity"])
        mechanism = str(known["mechanism"])
        clinical_effect = str(known["clinical_effect"])
        recommendation = str(known["recommendation"])
        source = "Known curated interaction database"
        detected = True

        severity_probability = {
            "Major": max(probability, 0.90),
            "Moderate": max(probability, 0.65),
            "Minor": max(probability, 0.40),
        }
        probability = severity_probability.get(severity, probability)
    else:
        severity = probability_to_severity(probability)
        detected = probability >= 0.45
        source = "Machine-learning prototype prediction"
        mechanism = "Predicted from structured prototype drug-risk features."
        clinical_effect = (
            "Potential interaction risk requires pharmacist or clinician review."
            if detected
            else "No significant interaction predicted by this prototype model."
        )
        recommendation = (
            "Review the combination with a qualified healthcare professional."
            if detected
            else "Continue normal clinical verification; this result is not medical advice."
        )

    alternative = (
        f"For {drug_a['drug_name']}: {drug_a['alternative']}. "
        f"For {drug_b['drug_name']}: {drug_b['alternative']}."
    )

    return {
        "drug_a": drug_a["drug_name"],
        "drug_b": drug_b["drug_name"],
        "interaction_detected": detected,
        "source": source,
        "risk_probability": round(probability, 3),
        "severity": severity,
        "mechanism": mechanism,
        "clinical_effect": clinical_effect,
        "recommendation": recommendation,
        "safer_alternative": alternative,
        "explanation": create_explanation(features),
    }