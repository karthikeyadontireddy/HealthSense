from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from backend.ml.training.common import candidate_models, evaluate, make_pipeline
from backend.ml.training.train_ckd import CATEGORICAL as CKD_CATEGORICAL
from backend.ml.training.train_ckd import NUMERIC as CKD_NUMERIC
from backend.ml.training.train_ckd import load_dataset as load_ckd
from backend.ml.training.train_diabetes import FEATURES as DIABETES_FEATURES
from backend.ml.training.train_diabetes import load_dataset as load_diabetes
from backend.ml.training.train_heart import CATEGORICAL as HEART_CATEGORICAL
from backend.ml.training.train_heart import NUMERIC as HEART_NUMERIC
from backend.ml.training.train_heart import load_dataset as load_heart

RESULTS_DIR = ROOT / "experiments" / "results"
SEED = 42
CV_SPLITS = 5
SELECTED = {
    "diabetes": "logistic_regression",
    "heart_disease": "logistic_regression",
    "ckd": "random_forest",
}
ABLATION_FEATURES = {
    "diabetes": ["Glucose", "BMI", "Age"],
    "heart_disease": ["ca", "cp", "thal"],
    "ckd": ["hemo", "sc", "pcv", "al", "rbcc"],
}


def calibration_error(y_true, probabilities, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    error = 0.0
    curve = []
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (probabilities >= lower) & ((probabilities < upper) if upper < 1 else (probabilities <= upper))
        if not mask.any():
            continue
        observed = float(np.mean(np.asarray(y_true)[mask]))
        predicted = float(np.mean(probabilities[mask]))
        error += abs(observed - predicted) * int(mask.sum()) / len(y_true)
        curve.append({"mean_predicted": predicted, "observed_fraction_positive": observed, "count": int(mask.sum())})
    return float(error), curve


def split_metrics(model_name, features, target, numeric, categorical):
    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.2, stratify=target, random_state=SEED)
    model = make_pipeline(model_name, candidate_models(SEED)[model_name], numeric, categorical)
    model.fit(x_train, y_train)
    result = evaluate(model, x_test, y_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    ece, curve = calibration_error(y_test.to_numpy(), probabilities)
    result.update({"brier_score": float(brier_score_loss(y_test, probabilities)), "expected_calibration_error": ece, "calibration_curve": curve})
    return result


def cv_metrics(model_name, features, target, numeric, categorical):
    training_features, _, training_target, _ = train_test_split(
        features, target, test_size=0.2, stratify=target, random_state=SEED
    )
    cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SEED)
    rows = []
    for train_indices, validation_indices in cv.split(training_features, training_target):
        x_train = training_features.iloc[train_indices]
        x_validation = training_features.iloc[validation_indices]
        y_train = training_target.iloc[train_indices]
        y_validation = training_target.iloc[validation_indices]
        model = make_pipeline(model_name, candidate_models(SEED)[model_name], numeric, categorical)
        model.fit(x_train, y_train)
        metrics = evaluate(model, x_validation, y_validation)
        probabilities = model.predict_proba(x_validation)[:, 1]
        ece, _ = calibration_error(y_validation.to_numpy(), probabilities)
        metrics.update({"brier_score": float(brier_score_loss(y_validation, probabilities)), "expected_calibration_error": ece})
        rows.append(metrics)
    metric_names = ["accuracy", "precision", "recall", "f1", "roc_auc", "brier_score", "expected_calibration_error"]
    return {
        "mean": {name: float(np.mean([row[name] for row in rows])) for name in metric_names},
        "std": {name: float(np.std([row[name] for row in rows], ddof=1)) for name in metric_names},
    }


def run_model_comparison(disease, features, target, numeric, categorical):
    return {
        model_name: {
            "cv": cv_metrics(model_name, features, target, numeric, categorical),
            "held_out_test_seed_42": split_metrics(model_name, features, target, numeric, categorical),
        }
        for model_name in candidate_models(SEED)
    }


def run_ablation(disease, features, target, numeric, categorical):
    selected = SELECTED[disease]
    rows = []
    variants = [("full_feature_set", None)] + [(f"remove_{feature}", feature) for feature in ABLATION_FEATURES[disease]]
    for name, removed in variants:
        variant_features = features.drop(columns=[removed]) if removed else features.copy()
        variant_numeric = [feature for feature in numeric if feature != removed]
        variant_categorical = [feature for feature in categorical if feature != removed]
        rows.append({
            "variant": name,
            "removed_feature": removed,
            "features": list(variant_features.columns),
            "cv": cv_metrics(selected, variant_features, target, variant_numeric, variant_categorical),
            "held_out_test_seed_42": split_metrics(selected, variant_features, target, variant_numeric, variant_categorical),
        })
    return rows


def main():
    diabetes_features, diabetes_target = load_diabetes()
    heart_features, heart_target = load_heart()
    ckd_features, ckd_target, ckd_dropped = load_ckd()
    datasets = {
        "diabetes": (diabetes_features, diabetes_target, DIABETES_FEATURES, []),
        "heart_disease": (heart_features, heart_target, HEART_NUMERIC, HEART_CATEGORICAL),
        "ckd": (ckd_features, ckd_target, CKD_NUMERIC, CKD_CATEGORICAL),
    }
    output = {
        "experiment_id": "controlled_ml_experiments",
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "cv_splits": CV_SPLITS,
        "selection_policy": "Existing selected baseline model is retained for ablation; candidate comparison does not rewrite production artifacts.",
        "dataset_policy": {"ckd_selected_source": "backend/datasets/ckd/original/chronic_kidney_disease.arff", "ckd_rejected_rows": ckd_dropped},
        "diseases": {},
    }
    for disease, (features, target, numeric, categorical) in datasets.items():
        output["diseases"][disease] = {
            "sample_count": int(len(features)),
            "class_counts": {str(key): int(value) for key, value in target.value_counts().sort_index().items()},
            "feature_names": list(features.columns),
            "numeric_features": numeric,
            "categorical_features": categorical,
            "selected_model": SELECTED[disease],
            "model_comparison": run_model_comparison(disease, features, target, numeric, categorical),
            "feature_ablation": run_ablation(disease, features, target, numeric, categorical),
        }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stem = RESULTS_DIR / f"controlled_ml_experiments_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    result_path = stem.with_suffix(".json")
    result_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Saved controlled experiment results to {result_path}")
    for disease, result in output["diseases"].items():
        print(disease, "selected", result["selected_model"])
        for variant in result["feature_ablation"]:
            metrics = variant["held_out_test_seed_42"]
            print(" ", variant["variant"], {name: round(metrics[name], 4) for name in ["accuracy", "precision", "recall", "f1", "roc_auc", "brier_score"]})


if __name__ == "__main__":
    main()
