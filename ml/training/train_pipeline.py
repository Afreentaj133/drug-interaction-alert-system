"""
Model Training, Multi-Algorithm Benchmark Comparison, and SHAP Explainer Pipeline.
Trains Logistic Regression, Random Forest, and XGBoost on RDKit-engineered features.
Evaluates Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, and Confusion Matrix.
Serializes the champion model artifact and SHAP TreeExplainer for sub-second API serving.
"""
from datetime import datetime
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, classification_report
)

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.preprocessing.extract_features import (
    FEATURE_COLUMNS, FEATURE_LABELS, create_pair_feature_vector
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "ml" / "data"
MODELS_DIR = BASE_DIR / "ml" / "models"
EVAL_DIR = BASE_DIR / "ml" / "evaluation"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

def build_training_matrix():
    drugs_df = pd.read_csv(DATA_DIR / "drugs_database.csv")
    interactions_df = pd.read_csv(DATA_DIR / "interactions_database.csv")

    drugs_lookup = {
        row["name"].strip().lower(): row.to_dict()
        for _, row in drugs_df.iterrows()
    }

    X_rows = []
    y_labels = []
    metadata_rows = []

    for _, row in interactions_df.iterrows():
        a_name = str(row["drug_a"]).strip().lower()
        b_name = str(row["drug_b"]).strip().lower()

        if a_name not in drugs_lookup or b_name not in drugs_lookup:
            continue

        drug_a = drugs_lookup[a_name]
        drug_b = drugs_lookup[b_name]

        feature_vector = create_pair_feature_vector(drug_a, drug_b)
        X_rows.append(feature_vector)
        y_labels.append(int(row["interaction"]))
        metadata_rows.append({
            "drug_a": row["drug_a"],
            "drug_b": row["drug_b"],
            "severity": row["severity"]
        })

    X = pd.DataFrame(X_rows)[FEATURE_COLUMNS]
    y = np.array(y_labels)

    return X, y, metadata_rows

def evaluate_model(name: str, model, X_test, y_test) -> dict:
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, preds))
    prec = float(precision_score(y_test, preds, zero_division=0))
    rec = float(recall_score(y_test, preds, zero_division=0))
    f1 = float(f1_score(y_test, preds, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, probs))
    pr_auc = float(average_precision_score(y_test, probs))
    cm = confusion_matrix(y_test, preds).tolist()

    return {
        "model_name": name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": cm,
        "classification_report": classification_report(y_test, preds, output_dict=True, zero_division=0)
    }

def main():
    print("=" * 70)
    print("  EXPLAINABLE MULTI-FEATURE DRUG INTERACTION RISK PREDICTION FRAMEWORK")
    print("=" * 70)

    print("[*] Assembling RDKit feature matrix from curated drug data...")
    X, y, metadata = build_training_matrix()
    print(f"[+] Total samples: {len(X)} | Positives (Interactions): {sum(y == 1)} | Negatives: {sum(y == 0)}")
    print(f"[+] Dimensionality: {X.shape[1]} engineered features (RDKit Morgan Fingerprint similarity + descriptors + pharmacology)")

    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    print(f"[+] Split: {len(X_train)} training pairs, {len(X_test)} hold-out evaluation pairs")

    # Define Candidate Models
    models = {
        "Logistic Regression (Baseline)": LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=42
        ),
        "Random Forest (Ensemble)": RandomForestClassifier(
            n_estimators=300, max_depth=6, min_samples_leaf=1,
            class_weight="balanced_subsample", random_state=42
        ),
        "XGBoost (Advanced Gradient Boosting)": XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.08,
            scale_pos_weight=3.3,
            eval_metric="logloss", random_state=42
        )
    }

    results = {}
    fitted_models = {}

    print("\n[*] Training and benchmarking multi-model candidates...")
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        fitted_models[name] = clf
        metrics = evaluate_model(name, clf, X_test, y_test)
        results[name] = metrics
        print(f"\n--- {name} ---")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1-Score:  {metrics['f1_score']:.4f}")
        print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"  PR-AUC:    {metrics['pr_auc']:.4f}")
        print(f"  Confusion Matrix: {metrics['confusion_matrix']}")

    # Select Champion Model (Primary criteria: ROC-AUC, Secondary: F1-Score)
    champion_name = max(results.keys(), key=lambda k: (results[k]["roc_auc"], results[k]["f1_score"]))
    champion_model = fitted_models[champion_name]
    print(f"\n[+] Champion Model Selected: {champion_name}")

    # Compute Feature Importances
    if hasattr(champion_model, "feature_importances_"):
        importances = {
            col: round(float(imp), 4)
            for col, imp in zip(FEATURE_COLUMNS, champion_model.feature_importances_)
        }
    else:
        # Logistic regression coefficients
        importances = {
            col: round(float(abs(coef)), 4)
            for col, coef in zip(FEATURE_COLUMNS, champion_model.coef_[0])
        }

    # Initialize SHAP Explainer
    print("\n[*] Initializing and serializing SHAP TreeExplainer for sub-second API interpretability...")
    if "Logistic" in champion_name:
        explainer = shap.LinearExplainer(champion_model, X_train)
    else:
        explainer = shap.TreeExplainer(champion_model)

    # Serialize Artifacts
    model_artifact = {
        "model": champion_model,
        "model_name": champion_name,
        "feature_columns": FEATURE_COLUMNS,
        "feature_labels": FEATURE_LABELS,
        "feature_importances": importances,
        "threshold": 0.50,
        "training_timestamp": datetime.now().isoformat(),
        "training_samples": len(X_train),
        "test_metrics": results[champion_name]
    }

    model_path = MODELS_DIR / "champion_model.joblib"
    joblib.dump(model_artifact, model_path)
    print(f"[+] Saved champion model artifact to {model_path}")

    explainer_path = MODELS_DIR / "shap_explainer.joblib"
    joblib.dump(explainer, explainer_path)
    print(f"[+] Saved SHAP explainer to {explainer_path}")

    # Save Evaluation Summary to JSON
    benchmark_report = {
        "generated_at": datetime.now().isoformat(),
        "total_dataset_size": len(X),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features_used": FEATURE_COLUMNS,
        "champion_model": champion_name,
        "models_benchmark": results,
        "feature_importances_ranked": sorted(importances.items(), key=lambda x: x[1], reverse=True)
    }

    metrics_path = EVAL_DIR / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(benchmark_report, f, indent=2)
    print(f"[+] Saved complete benchmark metrics to {metrics_path}")
    print("\n[OK] ML Pipeline Phase Completed Successfully!")

if __name__ == "__main__":
    main()
