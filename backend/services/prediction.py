from pathlib import Path

import joblib
import pandas as pd

from backend.config import MODEL_PATH

MODEL = None
MODEL_BUNDLE = None
# Exact features used by the trained Random Forest model for diabetes risk prediction
FEATURE_COLUMNS = ["Glucose", "BloodPressure", "Insulin", "BMI", "Age"]
DISEASE_NAME = "diabetes"
MODEL_NAME = "RandomForestClassifier"
MODEL_VERSION = "baseline_v1"

# Model Metadata
MODEL_DESCRIPTION = {
    "disease": "Diabetes",
    "algorithm": "Random Forest Classifier (200 trees)",
    "features": FEATURE_COLUMNS,
    "dataset": "Loaded from the trained model bundle",
}


def load_model():
    """Load the trained diabetes model.
    
    Automatically trains the model on first load if not found.
    Returns the scikit-learn RandomForestClassifier.
    """
    global MODEL, MODEL_BUNDLE, FEATURE_COLUMNS, MODEL_NAME, MODEL_VERSION, MODEL_DESCRIPTION
    if MODEL is None:
        if not MODEL_PATH.exists():
            from backend.ml import train_model
            train_model.train()
        bundle = joblib.load(MODEL_PATH)
        if not isinstance(bundle, dict) or "model" not in bundle:
            raise ValueError("The saved diabetes model is missing its metadata bundle.")
        MODEL_BUNDLE = bundle
        MODEL = bundle["model"]
        FEATURE_COLUMNS = bundle["feature_columns"]
        MODEL_VERSION = bundle.get("model_version", MODEL_VERSION)
        MODEL_NAME = type(MODEL).__name__
        MODEL_DESCRIPTION = bundle
    return MODEL


def predict_risk(age: float, glucose: float, blood_pressure: float, insulin: float, bmi: float):
    """Predict diabetes risk using the trained Random Forest model.
    
    Args:
        age: Patient age in years
        glucose: Fasting glucose in mg/dL
        blood_pressure: Systolic blood pressure in mmHg
        insulin: Fasting insulin in mU/ml
        bmi: Body Mass Index in kg/m²
    
    Returns:
        Tuple of (percentage, level, recommendations, disease_name, model_name, model_version)
    
    Note:
        This is a machine-learning model prediction for research/educational purposes.
        Not a medical diagnosis. Results should not be used for clinical decision-making.
    """
    model = load_model()
    features = pd.DataFrame([[glucose, blood_pressure, insulin, bmi, age]], columns=FEATURE_COLUMNS)
    probability = model.predict_proba(features)[0][1]
    percentage = round(float(probability * 100), 1)
    
    if probability < 0.3:
        level = "Low Risk"
        recommendations = [
            "This model-estimated probability is low. Continue routine health monitoring.",
            "Maintain healthy lifestyle habits including regular physical activity and balanced nutrition.",
        ]
    elif probability < 0.7:
        level = "Moderate Risk"
        recommendations = [
            "This model-estimated probability is moderate. Consider discussing results with a healthcare professional.",
            "Monitor key health indicators over time and maintain healthy lifestyle practices.",
        ]
    else:
        level = "High Risk"
        recommendations = [
            "This model-estimated probability is high. Consult with a healthcare professional for personalized guidance.",
            "Consider scheduling a comprehensive health assessment and discussing preventive strategies.",
        ]

    return percentage, level, recommendations, DISEASE_NAME, MODEL_NAME, MODEL_VERSION
