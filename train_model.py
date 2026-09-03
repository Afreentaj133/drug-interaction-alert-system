from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

FEATURE_COLUMNS = [
    "same_class",
    "both_cyp3a4_related",
    "cyp_inhibitor_substrate_pair",
    "both_qt_prolonging",
    "both_bleeding_risk",
    "both_serotonergic",
    "both_renal_risk",
    "drug_a_cyp_inhibitor",
    "drug_b_cyp_inhibitor",
    "drug_a_qt",
    "drug_b_qt",
]

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

def main():
    drugs = pd.read_csv(DATA_DIR / "drugs.csv")
    interactions = pd.read_csv(DATA_DIR / "interactions.csv")

    drugs_lookup = {
        row["drug_name"].strip().lower(): row
        for _, row in drugs.iterrows()
    }

    known_pairs = set()
    training_rows = []

    for _, interaction in interactions.iterrows():
        a = interaction["drug_a"].strip().lower()
        b = interaction["drug_b"].strip().lower()

        if a not in drugs_lookup or b not in drugs_lookup:
            continue

        known_pairs.add(tuple(sorted([a, b])))

        features = create_pair_features(drugs_lookup[a], drugs_lookup[b])
        features["label"] = 1
        training_rows.append(features)

    drug_names = list(drugs_lookup.keys())

    for i, name_a in enumerate(drug_names):
        for name_b in drug_names[i + 1:]:
            pair_key = tuple(sorted([name_a, name_b]))

            if pair_key in known_pairs:
                continue

            features = create_pair_features(
                drugs_lookup[name_a],
                drugs_lookup[name_b]
            )
            features["label"] = 0
            training_rows.append(features)

    dataset = pd.DataFrame(training_rows)

    positives = dataset[dataset["label"] == 1]
    negatives = dataset[dataset["label"] == 0].sample(
        n=min(len(dataset[dataset["label"] == 0]), len(positives) * 4),
        random_state=42
    )

    balanced_data = pd.concat([positives, negatives], ignore_index=True)
    X = balanced_data[FEATURE_COLUMNS]
    y = balanced_data["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        stratify=y,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("\nModel evaluation")
    print(classification_report(y_test, predictions, zero_division=0))

    if len(np.unique(y_test)) > 1:
        print("AUC-ROC:", round(roc_auc_score(y_test, probabilities), 3))

    MODEL_DIR.mkdir(exist_ok=True)

    artifact = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "feature_importance": dict(
            zip(FEATURE_COLUMNS, model.feature_importances_)
        )
    }

    joblib.dump(artifact, MODEL_DIR / "ddi_model.joblib")
    print("\nSaved model: models/ddi_model.joblib")

if __name__ == "__main__":
    main()

