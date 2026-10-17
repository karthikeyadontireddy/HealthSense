from pathlib import Path

import pandas as pd

from backend.ml.training.common import train_and_save

DATA_PATH = Path(__file__).resolve().parents[1] / ".." / "datasets" / "heart" / "original" / "processed.cleveland.data"
COLUMNS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"]
FEATURES = COLUMNS[:-1]
NUMERIC = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]


def load_dataset():
    raw = pd.read_csv(DATA_PATH, header=None, names=COLUMNS, dtype=str)
    data = raw.replace("?", pd.NA).apply(pd.to_numeric, errors="coerce")
    if data.isna()["num"].any() or not set(data["num"].dropna().unique()).issubset({0, 1, 2, 3, 4}):
        raise ValueError("Unexpected Heart target values")
    data["num"] = (data["num"] > 0).astype(int)
    return data[FEATURES], data["num"]


def train():
    features, target = load_dataset()
    return train_and_save(
        disease_id="heart_disease",
        display_name="Heart Disease Risk",
        dataset_name="UCI Heart Disease Cleveland subset",
        dataset_source="backend/datasets/heart/original/processed.cleveland.data",
        target_name="num_binary",
        feature_names=FEATURES,
        numeric_features=NUMERIC,
        categorical_features=CATEGORICAL,
        features=features,
        target=target,
        output_dir=Path(__file__).resolve().parents[1] / "models" / "heart",
        model_version="research_v1",
        preprocessing_description="Literal ? values become missing; median imputation is fitted on training data for numeric fields and most-frequent imputation plus one-hot encoding is fitted on training data for coded categorical fields.",
        dataset_policy="Original target num is documented as 0 versus 1-4. Training uses the deliberate binary mapping num=0 -> 0 and num=1,2,3,4 -> 1.",
        limitations=["Small single-site subset", "Binary target transformation is a research choice", "No clinical validation", "Model probability calibration was not evaluated"],
    )


if __name__ == "__main__":
    train()
