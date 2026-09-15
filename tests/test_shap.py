from backend.app.ml.explainer import explainer_service
from ml.preprocessing.extract_features import FEATURE_COLUMNS

def test_shap_explanation_structure():
    # Synthetic feature vector simulating a high-risk pair
    test_features = {col: 0.0 for col in FEATURE_COLUMNS}
    test_features["both_bleeding_risk"] = 1.0
    test_features["any_bleeding_risk"] = 1.0
    test_features["tanimoto_similarity"] = 0.45
    test_features["mw_diff"] = 120.0

    contributions = explainer_service.explain_instance(test_features, top_k=5)
    assert len(contributions) > 0
    assert len(contributions) <= 5

    first = contributions[0]
    assert hasattr(first, "feature_name")
    assert hasattr(first, "feature_label")
    assert hasattr(first, "shap_value")
    assert hasattr(first, "impact")
    assert first.impact in ["Increases Risk", "Decreases Risk"]

    # Verify descending ordering by absolute magnitude
    for i in range(len(contributions) - 1):
        assert abs(contributions[i].shap_value) >= abs(contributions[i+1].shap_value)
