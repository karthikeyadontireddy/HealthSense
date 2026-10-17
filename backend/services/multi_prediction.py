from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any

import joblib
import pandas as pd

from backend.ml.model_registry import DiseaseModelConfig, get_model_config


_CACHE: dict[str, dict[str, Any]] = {}


def load_bundle(disease_id: str) -> tuple[DiseaseModelConfig, dict[str, Any]]:
    config = get_model_config(disease_id)
    if not config.model_path.exists():
        raise FileNotFoundError(f"No trained model artifact is available for {disease_id}.")
    if disease_id not in _CACHE:
        _CACHE[disease_id] = joblib.load(config.model_path)
    return config, _CACHE[disease_id]


def validate_features(config: DiseaseModelConfig, features: dict[str, Any], bundle: dict[str, Any]) -> None:
    expected = set(config.feature_names)
    supplied = set(features)
    missing = sorted(expected - supplied)
    unknown = sorted(supplied - expected)
    if missing:
        raise ValueError(f"Missing required features: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"Unknown features: {', '.join(unknown)}")
    for name, value in features.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Feature '{name}' cannot be empty.")
        if name in config.numeric_features:
            try:
                numeric_value = float(value)
            except (TypeError, ValueError) as error:
                raise ValueError(f"Feature '{name}' must be numeric.") from error
            if not math.isfinite(numeric_value):
                raise ValueError(f"Feature '{name}' must be finite.")
            if numeric_value < 0:
                raise ValueError(f"Feature '{name}' cannot be negative.")

    if config.categorical_features:
        encoder = bundle["pipeline"].named_steps["preprocess"].named_transformers_["categorical"].named_steps["encoder"]
        categories = dict(zip(config.categorical_features, encoder.categories_))
        for name in config.categorical_features:
            def matches(option):
                try:
                    return float(features[name]) == float(option)
                except (TypeError, ValueError):
                    return str(features[name]) == str(option)

            if name in categories and not any(matches(option) for option in categories[name]):
                raise ValueError(f"Feature '{name}' has an invalid categorical value.")


def predict(disease_id: str, features: dict[str, Any]) -> dict[str, Any]:
    config, bundle = load_bundle(disease_id)
    validate_features(config, features, bundle)
    pipeline = bundle["pipeline"]
    frame = pd.DataFrame([features], columns=list(config.feature_names))
    predicted = pipeline.predict(frame)[0]
    probabilities = None
    positive_probability = None
    if hasattr(pipeline, "predict_proba"):
        probabilities_array = pipeline.predict_proba(frame)[0]
        classes = list(pipeline.classes_)
        probabilities = {str(label): round(float(value), 6) for label, value in zip(classes, probabilities_array)}
        if len(probabilities_array) == 2:
            positive_index = classes.index(1) if 1 in classes else 1
            positive_probability = float(probabilities_array[positive_index])
    risk_level = None
    if positive_probability is not None:
        risk_level = "Low model-estimated risk" if positive_probability < 0.3 else "Moderate model-estimated risk" if positive_probability < 0.7 else "High model-estimated risk"
    return {
        "disease": config.disease_id,
        "display_name": config.display_name,
        "model_name": config.model_name,
        "model_version": config.model_version,
        "prediction_class": int(predicted) if hasattr(predicted, "item") and str(predicted).isdigit() else str(predicted),
        "probabilities": probabilities,
        "positive_class_probability": round(positive_probability, 6) if positive_probability is not None else None,
        "risk_level": risk_level,
        "feature_importance": bundle["metadata"].get("feature_importance", []),
        "research_disclaimer": "Research/educational ML output only. This does not establish whether a person has a medical condition and is not a medical diagnosis.",
        "created_at": datetime.now(timezone.utc),
    }
