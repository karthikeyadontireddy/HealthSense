import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
import joblib

from backend.config import MODEL_PATH

DATA_URL = "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv"
FEATURE_COLUMNS = ["Glucose", "BloodPressure", "Insulin", "BMI", "Age"]
TARGET_COLUMN = "Outcome"
MODEL_VERSION = "baseline_v1"
RANDOM_STATE = 42
TEST_SIZE = 0.2
MODEL_HYPERPARAMETERS = {
    "n_estimators": 200,
    "class_weight": "balanced",
    "random_state": RANDOM_STATE,
}


def load_data():
    df = pd.read_csv(DATA_URL)
    return df[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()


def train():
    data = load_data()
    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    model = RandomForestClassifier(**MODEL_HYPERPARAMETERS)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_prob),
    }

    model_bundle = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "dataset": {
            "name": "Plotly diabetes dataset",
            "source": DATA_URL,
            "rows": len(data),
        },
        "task": "binary classification",
        "preprocessing": "None; raw feature values are used directly.",
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "test_size": TEST_SIZE,
        "stratified": True,
        "random_state": RANDOM_STATE,
        "model_version": MODEL_VERSION,
        "hyperparameters": MODEL_HYPERPARAMETERS,
        "metrics": metrics,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_bundle, MODEL_PATH)

    print("Model training summary:")
    for name, value in metrics.items():
        print(f"- {name}: {value:.4f}")
    print(f"Saved trained model to {MODEL_PATH}")
    return model_bundle


if __name__ == "__main__":
    train()
