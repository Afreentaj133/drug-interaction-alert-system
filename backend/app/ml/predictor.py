from typing import Optional, Dict, Any, Tuple
import joblib
import pandas as pd
from backend.app.utils.config import settings
from backend.app.utils.logger import logger
from ml.preprocessing.extract_features import FEATURE_COLUMNS, FEATURE_LABELS, create_pair_feature_vector

class MLPredictor:
    def __init__(self):
        self.model = None
        self.model_name = "Random Forest (Ensemble)"
        self.feature_columns = FEATURE_COLUMNS
        self.feature_labels = FEATURE_LABELS
        self.threshold = 0.50
        self.metadata = {}
        self._load_model()

    def _load_model(self):
        if settings.MODEL_PATH.exists():
            try:
                artifact = joblib.load(settings.MODEL_PATH)
                self.model = artifact.get("model")
                self.model_name = artifact.get("model_name", "Random Forest (Ensemble)")
                self.feature_columns = artifact.get("feature_columns", FEATURE_COLUMNS)
                self.feature_labels = artifact.get("feature_labels", FEATURE_LABELS)
                self.threshold = artifact.get("threshold", 0.50)
                self.metadata = {
                    "training_timestamp": artifact.get("training_timestamp"),
                    "training_samples": artifact.get("training_samples"),
                    "metrics": artifact.get("test_metrics"),
                    "feature_importances": artifact.get("feature_importances", {})
                }
                logger.info(f"Loaded ML model: {self.model_name} from {settings.MODEL_PATH}")
            except Exception as e:
                logger.error(f"Error loading ML model from {settings.MODEL_PATH}: {e}")
        else:
            logger.warning(f"Model file not found at {settings.MODEL_PATH}. Running in fallback heuristic mode.")

    def predict_pair(self, drug_a: Dict[str, Any], drug_b: Dict[str, Any]) -> Tuple[float, Dict[str, float], bool]:
        """
        Extract features and compute interaction probability.
        Returns: (probability, feature_dict, is_ml_prediction)
        """
        features = create_pair_feature_vector(drug_a, drug_b)
        
        if self.model is not None:
            feature_df = pd.DataFrame([features])[self.feature_columns]
            try:
                probs = self.model.predict_proba(feature_df)[0]
                prob = float(probs[1])
                return round(prob, 4), features, True
            except Exception as e:
                logger.error(f"Error during ML inference: {e}")

        # Safe heuristic fallback if model is unavailable
        risk_score = 0.10
        if features.get("cyp_inhibitor_substrate_pair", 0):
            risk_score += 0.40
        if features.get("both_bleeding_risk", 0):
            risk_score += 0.45
        if features.get("both_qt_prolonging", 0):
            risk_score += 0.40
        if features.get("both_serotonergic", 0):
            risk_score += 0.35
        if features.get("both_renal_risk", 0):
            risk_score += 0.25
        if features.get("tanimoto_similarity", 0.0) > 0.35:
            risk_score += 0.15
            
        prob = min(max(risk_score, 0.05), 0.95)
        return round(prob, 4), features, False

predictor = MLPredictor()
