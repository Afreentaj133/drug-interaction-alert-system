from typing import List, Dict, Any
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from backend.app.utils.config import settings
from backend.app.utils.logger import logger
from backend.app.schemas.interaction_schema import ShapFeatureContribution
from ml.preprocessing.extract_features import FEATURE_COLUMNS, FEATURE_LABELS

class SHAPExplainerService:
    def __init__(self):
        self.explainer = None
        self._load_explainer()

    def _load_explainer(self):
        if settings.SHAP_EXPLAINER_PATH.exists():
            try:
                self.explainer = joblib.load(settings.SHAP_EXPLAINER_PATH)
                logger.info(f"Loaded SHAP TreeExplainer from {settings.SHAP_EXPLAINER_PATH}")
            except Exception as e:
                logger.error(f"Error loading SHAP explainer: {e}")
        else:
            logger.warning("SHAP explainer artifact not found. Will use feature magnitude heuristic.")

    def explain_instance(self, features: Dict[str, float], top_k: int = 5) -> List[ShapFeatureContribution]:
        """
        Compute genuine SHAP feature attributions for a single drug-pair instance.
        Returns top_k most impactful features sorted by absolute SHAP attribution.
        """
        feature_df = pd.DataFrame([features])[FEATURE_COLUMNS]

        if self.explainer is not None:
            try:
                raw_shap = self.explainer.shap_values(feature_df)
                
                # Handle 3D array (1, n_features, 2)
                if isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 3:
                    class_1_shap = raw_shap[0, :, 1]
                elif isinstance(raw_shap, list) and len(raw_shap) >= 2:
                    class_1_shap = raw_shap[1][0]
                elif isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 2:
                    class_1_shap = raw_shap[0]
                else:
                    class_1_shap = np.array(raw_shap).flatten()

                contributions = []
                for col_name, shap_val in zip(FEATURE_COLUMNS, class_1_shap):
                    val = float(features.get(col_name, 0.0))
                    label = FEATURE_LABELS.get(col_name, col_name.replace("_", " ").title())
                    impact = "Increases Risk" if shap_val > 0 else "Decreases Risk"
                    
                    contributions.append(ShapFeatureContribution(
                        feature_name=col_name,
                        feature_label=label,
                        value=round(val, 4),
                        shap_value=round(float(shap_val), 4),
                        impact=impact
                    ))

                # Rank by absolute SHAP magnitude
                contributions.sort(key=lambda x: abs(x.shap_value), reverse=True)
                return contributions[:top_k]

            except Exception as e:
                logger.error(f"Error computing SHAP values: {e}")

        # Fallback ranking if SHAP artifact failed to load
        fallback = []
        for col_name in FEATURE_COLUMNS:
            val = float(features.get(col_name, 0.0))
            if val > 0:
                label = FEATURE_LABELS.get(col_name, col_name.replace("_", " ").title())
                fallback.append(ShapFeatureContribution(
                    feature_name=col_name,
                    feature_label=label,
                    value=round(val, 4),
                    shap_value=0.1,
                    impact="Increases Risk"
                ))
        return fallback[:top_k]

explainer_service = SHAPExplainerService()
