from pathlib import Path

import pandas as pd

from backend.ml.training.common import train_and_save

DATA_URL = "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv"
FEATURES = ["Glucose", "BloodPressure", "Insulin", "BMI", "Age"]
NUMERIC = FEATURES
TARGET = "Outcome"


def load_dataset():
    data = pd.read_csv(DATA_URL)
    expected = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"]
    if list(data.columns) != expected:
        raise ValueError(f"Unexpected Diabetes columns: {list(data.columns)}")
    if not set(data[TARGET].unique()).issubset({0, 1}):
        raise ValueError("Diabetes target must contain only 0 and 1")
    data = data.copy()
    for column in ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]:
        data.loc[data[column] == 0, column] = pd.NA
    return data[FEATURES], data[TARGET]


def train():
    features, target = load_dataset()
    return train_and_save(
        disease_id="diabetes",
        display_name="Diabetes Risk",
        dataset_name="Plotly diabetes dataset",
        dataset_source=DATA_URL,
        target_name=TARGET,
        feature_names=FEATURES,
        numeric_features=NUMERIC,
        categorical_features=[],
        features=features,
        target=target,
        output_dir=Path(__file__).resolve().parents[1] / "models" / "diabetes",
        model_version="research_v1",
        preprocessing_description="Selected zero-coded clinical measurements are treated as missing; median imputation is fitted on training data. Logistic Regression receives StandardScaler; tree models do not.",
        dataset_policy="Original remote CSV is read-only. Zero is treated as missing only for Glucose, BloodPressure, SkinThickness, Insulin, and BMI; zero Pregnancies is retained.",
        limitations=["Single public dataset", "No external validation", "Zero-coded values are a dataset convention requiring sensitivity analysis", "Model probability calibration was not evaluated", "HbA1c is not present in the source dataset"],
    )


if __name__ == "__main__":
    train()
