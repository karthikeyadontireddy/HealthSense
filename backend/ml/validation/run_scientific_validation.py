from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.calibration import calibration_curve
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from backend.ml.training.common import candidate_models, make_pipeline
from backend.ml.training.train_ckd import load_dataset as load_ckd
from backend.ml.training.train_diabetes import FEATURES as DIABETES_FEATURES
from backend.ml.training.train_diabetes import load_dataset as load_diabetes
from backend.ml.training.train_heart import CATEGORICAL as HEART_CATEGORICAL
from backend.ml.training.train_heart import NUMERIC as HEART_NUMERIC
from backend.ml.training.train_heart import load_dataset as load_heart
from backend.ml.training.common import evaluate

ROOT = Path(__file__).resolve().parents[2]
SEEDS = [42, 7, 21, 100, 2026]
METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]


def calibration_error(y_true, probabilities, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    total = len(y_true)
    error = 0.0
    rows = []
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (probabilities >= lower) & ((probabilities < upper) if upper < 1 else (probabilities <= upper))
        if not mask.any():
            continue
        observed = float(np.mean(np.asarray(y_true)[mask]))
        predicted = float(np.mean(probabilities[mask]))
        count = int(mask.sum())
        error += abs(observed - predicted) * count / total
        rows.append({"count": count, "mean_predicted": predicted, "observed_rate": observed})
    return float(error), rows


def evaluate_seed(model_name, features, target, numeric, categorical, seed):
    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.2, stratify=target, random_state=seed)
    model = make_pipeline(model_name, candidate_models(seed)[model_name], numeric, categorical)
    model.fit(x_train, y_train)
    metrics = evaluate(model, x_test, y_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    metrics["brier_score"] = float(brier_score_loss(y_test, probabilities))
    metrics["expected_calibration_error"] = calibration_error(y_test.to_numpy(), probabilities)[0]
    fraction_positive, mean_predicted = calibration_curve(y_test, probabilities, n_bins=10, strategy="uniform")
    metrics["calibration_curve"] = [
        {"mean_predicted": float(predicted), "observed_fraction_positive": float(observed)}
        for observed, predicted in zip(fraction_positive, mean_predicted)
    ]
    return metrics


def cross_validation(model_name, features, target, numeric, categorical):
    rows = []
    for seed in SEEDS:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        model = make_pipeline(model_name, candidate_models(seed)[model_name], numeric, categorical)
        scoring = {metric: metric for metric in METRICS}
        scores = cross_validate(model, features, target, cv=cv, scoring=scoring, error_score="raise")
        rows.append({metric: float(np.mean(scores[f"test_{metric}"])) for metric in METRICS})
    return {
        "per_seed": rows,
        "mean": {metric: float(np.mean([row[metric] for row in rows])) for metric in METRICS},
        "std": {metric: float(np.std([row[metric] for row in rows], ddof=1)) for metric in METRICS},
    }


def final_split_comparison(features, target, numeric, categorical):
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, stratify=target, random_state=42
    )
    results = {}
    for model_name, estimator in candidate_models(42).items():
        model = make_pipeline(model_name, estimator, numeric, categorical)
        model.fit(x_train, y_train)
        results[model_name] = evaluate(model, x_test, y_test)
    return results


def robustness(model_name, features, target, numeric, categorical):
    rows = [{"seed": seed, **evaluate_seed(model_name, features, target, numeric, categorical, seed)} for seed in SEEDS]
    return {
        "per_seed": rows,
        "mean": {metric: float(np.mean([row[metric] for row in rows])) for metric in METRICS},
        "std": {metric: float(np.std([row[metric] for row in rows], ddof=1)) for metric in METRICS},
        "calibration_mean": {metric: float(np.mean([row[metric] for row in rows])) for metric in ["brier_score", "expected_calibration_error"]},
        "calibration_std": {metric: float(np.std([row[metric] for row in rows], ddof=1)) for metric in ["brier_score", "expected_calibration_error"]},
    }


def ckd_diagnostics(features, target):
    diagnostics = {
        "class_counts": {str(k): int(v) for k, v in target.value_counts().sort_index().items()},
        "feature_duplicate_rows": int(features.duplicated().sum()),
        "top_model_features": json.loads((ROOT / "ml" / "models" / "ckd" / "metadata.json").read_text(encoding="utf-8"))["feature_importance"][:10],
        "numeric_separation": {},
        "categorical_separation": {},
        "split_feature_overlap_seed_42": None,
        "malformed_policy": "Three records with 26 fields were excluded; no valid inclusion/repair sensitivity alternative exists without deciding how the shifted row should be interpreted.",
    }
    for column in features.select_dtypes(include="number").columns:
        values = features[column].fillna(features[column].median())
        try:
            diagnostics["numeric_separation"][column] = float(roc_auc_score(target, values))
        except ValueError:
            diagnostics["numeric_separation"][column] = None
    for column in features.select_dtypes(exclude="number").columns:
        rates = pd.DataFrame({"value": features[column].fillna("<missing>"), "target": target}).groupby("value")["target"].agg(["count", "mean"]).to_dict("index")
        diagnostics["categorical_separation"][column] = {str(k): {"count": int(v["count"]), "positive_rate": float(v["mean"])} for k, v in rates.items()}
    train_index, test_index = train_test_split(np.arange(len(features)), test_size=0.2, stratify=target, random_state=42)
    train_features = features.iloc[train_index].astype(str)
    test_features = features.iloc[test_index].astype(str)
    train_keys = set(map(tuple, train_features.to_numpy().tolist()))
    test_keys = set(map(tuple, test_features.to_numpy().tolist()))
    diagnostics["split_feature_overlap_seed_42"] = len(train_keys & test_keys)
    return diagnostics


def dataset_entry(disease, features, target, model_name, numeric, categorical):
    return {
        "model_name": model_name,
        "class_counts": {str(k): int(v) for k, v in target.value_counts().sort_index().items()},
        "class_proportions": {str(k): float(v) for k, v in target.value_counts(normalize=True).sort_index().items()},
        "cross_validation": cross_validation(model_name, features, target, numeric, categorical),
        "final_split_candidate_comparison": final_split_comparison(features, target, numeric, categorical),
        "robustness": robustness(model_name, features, target, numeric, categorical),
    }


def main():
    diabetes_features, diabetes_target = load_diabetes()
    heart_features, heart_target = load_heart()
    ckd_features, ckd_target, dropped = load_ckd()
    diabetes_entry = dataset_entry("diabetes", diabetes_features, diabetes_target, "logistic_regression", DIABETES_FEATURES, [])
    raw_diabetes = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv")[DIABETES_FEATURES]
    diabetes_entry["zero_policy_sensitivity"] = {
        "documented_zero_as_missing": robustness("logistic_regression", diabetes_features, diabetes_target, DIABETES_FEATURES, []),
        "raw_zero_retained": robustness("logistic_regression", raw_diabetes, diabetes_target, DIABETES_FEATURES, []),
    }
    heart_entry = dataset_entry("heart_disease", heart_features, heart_target, "logistic_regression", HEART_NUMERIC, HEART_CATEGORICAL)
    ckd_entry = dataset_entry("ckd", ckd_features, ckd_target, "random_forest", list(ckd_features.select_dtypes(include="number").columns), list(ckd_features.select_dtypes(exclude="number").columns))
    ckd_entry["dropped_rows"] = dropped
    ckd_entry["diagnostics"] = ckd_diagnostics(ckd_features, ckd_target)
    output = {"date": "2026-09-07", "seeds": SEEDS, "diseases": {"diabetes": diabetes_entry, "heart_disease": heart_entry, "ckd": ckd_entry}}
    output_path = ROOT / "ml" / "validation" / "validation_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Saved validation results to {output_path}")
    for disease, result in output["diseases"].items():
        print(disease, "CV mean", result["cross_validation"]["mean"], "CV std", result["cross_validation"]["std"])
        print(disease, "robust mean", result["robustness"]["mean"], "robust std", result["robustness"]["std"])
        print(disease, "calibration", result["robustness"]["calibration_mean"])


if __name__ == "__main__":
    main()
