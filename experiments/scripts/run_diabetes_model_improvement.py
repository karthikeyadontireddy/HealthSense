"""Controlled Diabetes-only model improvement experiment.

This script never writes to backend/ml/models. It evaluates candidates using a
fixed stratified holdout and selects only from training-fold cross-validation.
"""
from __future__ import annotations

import json
import joblib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "experiments" / "results"
REPORT_PATH = ROOT / "DIABETES_MODEL_IMPROVEMENT.md"
DATA_URL = "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv"
EXPECTED_COLUMNS = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin",
    "BMI", "DiabetesPedigreeFunction", "Age", "Outcome",
]
ALL_FEATURES = EXPECTED_COLUMNS[:-1]
BASELINE_FEATURES = ["Glucose", "BloodPressure", "Insulin", "BMI", "Age"]
ZERO_AS_MISSING = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
SEEDS = [42, 7, 21, 100, 2026]
SELECTION_SEED = 42
TEST_SIZE = 0.2
CV_SPLITS = 5
METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc", "brier_score"]


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    feature_set: str
    features: tuple[str, ...]
    zero_policy: str
    imputation: str
    model_name: str
    class_weight: str | None
    scale_numeric: bool
    hyperparameters: dict[str, Any]


def load_raw_dataset() -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    data = pd.read_csv(DATA_URL)
    if list(data.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected Diabetes columns: {list(data.columns)}")
    if not set(data["Outcome"].unique()).issubset({0, 1}):
        raise ValueError("Diabetes target must contain only 0 and 1")
    zero_counts = {column: int((data[column] == 0).sum()) for column in ZERO_AS_MISSING}
    return data[ALL_FEATURES].copy(), data["Outcome"].copy(), {
        "source": DATA_URL,
        "shape": [int(data.shape[0]), int(data.shape[1])],
        "columns": EXPECTED_COLUMNS,
        "class_counts": {str(k): int(v) for k, v in data["Outcome"].value_counts().sort_index().items()},
        "zero_counts": zero_counts,
        "original_dataset_unchanged": True,
    }


def apply_zero_policy(features: pd.DataFrame, policy: str) -> pd.DataFrame:
    result = features.copy()
    if policy == "zero_as_missing":
        for column in [name for name in ZERO_AS_MISSING if name in result.columns]:
            result.loc[result[column] == 0, column] = np.nan
    elif policy != "raw_zeros":
        raise ValueError(f"Unknown zero policy: {policy}")
    return result


def make_candidate_pipeline(candidate: Candidate, seed: int) -> Pipeline:
    steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy=candidate.imputation))]
    if candidate.scale_numeric:
        steps.append(("scaler", StandardScaler()))
    params = candidate.hyperparameters
    if candidate.model_name == "logistic_regression":
        estimator = LogisticRegression(
            max_iter=2000,
            class_weight=None if candidate.class_weight == "none" else candidate.class_weight,
            random_state=seed,
            C=params["C"],
        )
    elif candidate.model_name == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            class_weight=None if candidate.class_weight == "none" else candidate.class_weight,
            random_state=seed,
            n_jobs=-1,
        )
    elif candidate.model_name == "gradient_boosting":
        estimator = GradientBoostingClassifier(
            n_estimators=params["n_estimators"],
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            random_state=seed,
        )
    else:
        raise ValueError(f"Unknown model: {candidate.model_name}")
    steps.append(("model", estimator))
    return Pipeline(steps)


def evaluate(model: Pipeline, features: pd.DataFrame, target: pd.Series) -> dict[str, Any]:
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]
    return {
        "accuracy": float(accuracy_score(target, predictions)),
        "precision": float(precision_score(target, predictions, zero_division=0)),
        "recall": float(recall_score(target, predictions, zero_division=0)),
        "f1": float(f1_score(target, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(target, probabilities)),
        "brier_score": float(brier_score_loss(target, probabilities)),
        "confusion_matrix": confusion_matrix(target, predictions).tolist(),
    }


def mean_std(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    return {
        "mean": {metric: float(np.mean([row[metric] for row in rows])) for metric in METRICS},
        "std": {metric: float(np.std([row[metric] for row in rows], ddof=1)) for metric in METRICS},
    }


def cross_validate_candidate(candidate: Candidate, train_features: pd.DataFrame, train_target: pd.Series) -> dict[str, Any]:
    splitter = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SELECTION_SEED)
    rows = []
    for fold, (train_indices, validation_indices) in enumerate(splitter.split(train_features, train_target), start=1):
        model = make_candidate_pipeline(candidate, SELECTION_SEED)
        model.fit(train_features.iloc[train_indices], train_target.iloc[train_indices])
        metrics = evaluate(model, train_features.iloc[validation_indices], train_target.iloc[validation_indices])
        metrics["fold"] = fold
        rows.append(metrics)
    summary = mean_std(rows)
    return {"folds": rows, **summary}


def holdout_evaluate(candidate: Candidate, train_features: pd.DataFrame, train_target: pd.Series, test_features: pd.DataFrame, test_target: pd.Series) -> dict[str, Any]:
    model = make_candidate_pipeline(candidate, SELECTION_SEED)
    model.fit(train_features, train_target)
    return evaluate(model, test_features, test_target)


def robustness(candidate: Candidate, features: pd.DataFrame, target: pd.Series) -> dict[str, Any]:
    rows = []
    for seed in SEEDS:
        train_indices, test_indices = train_test_split(
            np.arange(len(features)), test_size=TEST_SIZE, stratify=target, random_state=seed
        )
        model = make_candidate_pipeline(candidate, seed)
        model.fit(features.iloc[train_indices], target.iloc[train_indices])
        metrics = evaluate(model, features.iloc[test_indices], target.iloc[test_indices])
        rows.append({"seed": seed, **metrics})
    return {"per_seed": rows, **mean_std(rows)}


def build_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    feature_sets = [("current_5", tuple(BASELINE_FEATURES)), ("all_8", tuple(ALL_FEATURES))]
    for feature_set, features in feature_sets:
        for zero_policy in ("zero_as_missing", "raw_zeros"):
            imputations = ("median", "mean") if zero_policy == "zero_as_missing" else ("median",)
            for imputation in imputations:
                prefix = f"{feature_set}__{zero_policy}__{imputation}"
                candidates.extend([
                    Candidate(f"{prefix}__logistic__balanced__c0_1", feature_set, features, zero_policy, imputation, "logistic_regression", "balanced", True, {"C": 0.1}),
                    Candidate(f"{prefix}__logistic__balanced__c1", feature_set, features, zero_policy, imputation, "logistic_regression", "balanced", True, {"C": 1.0}),
                    Candidate(f"{prefix}__logistic__balanced__c10", feature_set, features, zero_policy, imputation, "logistic_regression", "balanced", True, {"C": 10.0}),
                    Candidate(f"{prefix}__logistic__unweighted__c1", feature_set, features, zero_policy, imputation, "logistic_regression", "none", True, {"C": 1.0}),
                    Candidate(f"{prefix}__logistic__balanced__c0_1__unscaled", feature_set, features, zero_policy, imputation, "logistic_regression", "balanced", False, {"C": 0.1}),
                    Candidate(f"{prefix}__logistic__balanced__c1__unscaled", feature_set, features, zero_policy, imputation, "logistic_regression", "balanced", False, {"C": 1.0}),
                    Candidate(f"{prefix}__logistic__balanced__c10__unscaled", feature_set, features, zero_policy, imputation, "logistic_regression", "balanced", False, {"C": 10.0}),
                    Candidate(f"{prefix}__logistic__unweighted__c1__unscaled", feature_set, features, zero_policy, imputation, "logistic_regression", "none", False, {"C": 1.0}),
                    Candidate(f"{prefix}__random_forest__balanced__depth4", feature_set, features, zero_policy, imputation, "random_forest", "balanced", False, {"n_estimators": 300, "max_depth": 4}),
                    Candidate(f"{prefix}__random_forest__balanced__unlimited", feature_set, features, zero_policy, imputation, "random_forest", "balanced", False, {"n_estimators": 300, "max_depth": None}),
                    Candidate(f"{prefix}__random_forest__unweighted__depth4", feature_set, features, zero_policy, imputation, "random_forest", "none", False, {"n_estimators": 300, "max_depth": 4}),
                    Candidate(f"{prefix}__gradient_boosting__lr005", feature_set, features, zero_policy, imputation, "gradient_boosting", "none", False, {"n_estimators": 200, "learning_rate": 0.05, "max_depth": 2}),
                    Candidate(f"{prefix}__gradient_boosting__lr01", feature_set, features, zero_policy, imputation, "gradient_boosting", "none", False, {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 2}),
                ])
    return candidates


def candidate_to_dict(candidate: Candidate) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "feature_set": candidate.feature_set,
        "features": list(candidate.features),
        "zero_policy": candidate.zero_policy,
        "imputation": candidate.imputation,
        "model_name": candidate.model_name,
        "class_weight": candidate.class_weight,
        "scale_numeric": candidate.scale_numeric,
        "hyperparameters": candidate.hyperparameters,
    }


def fmt(value: float) -> str:
    return f"{value:.4f}"


def report_markdown(result: dict[str, Any], candidates: list[Candidate]) -> str:
    baseline = result["baseline"]
    ranked = result["candidate_ranking"]
    best = ranked[0]
    best_candidate = result["candidates"][best["candidate_id"]]
    best_robust = result["robustness"][best["candidate_id"]]
    baseline_robust = result["robustness"][baseline["candidate_id"]]
    improvement = best["holdout"]["accuracy"] - baseline["holdout"]["accuracy"]
    scientifically_better = (
        best["cv"]["mean"]["roc_auc"] > baseline["cv"]["mean"]["roc_auc"]
        and best_robust["mean"]["roc_auc"] >= baseline_robust["mean"]["roc_auc"]
        and best_robust["mean"]["f1"] >= baseline_robust["mean"]["f1"]
    )
    lines = [
        "# Diabetes Model Improvement Experiment",
        "",
        f"Run timestamp: `{result['run_timestamp']}`  ",
        f"Source: `{DATA_URL}`  ",
        "Production artifact status: `research_v1` was not modified.",
        f"Review artifact: `{result.get('candidate_artifact', {}).get('path', 'not prepared')}` (`research_v2_candidate`, inactive).",
        "",
        "## Executive conclusion",
        "",
        f"The baseline is `{baseline['candidate_id']}`. The top candidate by training-only cross-validation ROC-AUC/F1 is `{best['candidate_id']}`.",
        f"On the fixed seed-42 holdout, the candidate accuracy is **{fmt(best['holdout']['accuracy'])}** versus **{fmt(baseline['holdout']['accuracy'])}** for baseline; F1 is **{fmt(best['holdout']['f1'])}** versus **{fmt(baseline['holdout']['f1'])}**, and ROC-AUC is **{fmt(best['holdout']['roc_auc'])}** versus **{fmt(baseline['holdout']['roc_auc'])}**.",
        f"Five-seed robustness gives candidate mean F1 **{fmt(best_robust['mean']['f1'])} +/- {fmt(best_robust['std']['f1'])}** and mean ROC-AUC **{fmt(best_robust['mean']['roc_auc'])} +/- {fmt(best_robust['std']['roc_auc'])}**, versus baseline F1 **{fmt(baseline_robust['mean']['f1'])} +/- {fmt(baseline_robust['std']['f1'])}** and ROC-AUC **{fmt(baseline_robust['mean']['roc_auc'])} +/- {fmt(baseline_robust['std']['roc_auc'])}**.",
        f"The candidate is {'scientifically preferable for further review' if scientifically_better else 'not demonstrated to be scientifically preferable'}; this is not approval to replace production. The fixed-holdout accuracy difference is {improvement:+.4f}, and no claim of 85% accuracy is made.",
        "",
        "## Baseline",
        "",
        "- Model: Logistic Regression, class-weight balanced, `C=1.0`.",
        "- Features: Glucose, BloodPressure, Insulin, BMI, Age.",
        "- Zero policy: Glucose, BloodPressure, SkinThickness, Insulin, and BMI zeros become missing; median imputation is fitted within each training pipeline.",
        "- Scaling: StandardScaler inside the Logistic Regression pipeline.",
        f"- Fixed holdout: accuracy {fmt(baseline['holdout']['accuracy'])}, precision {fmt(baseline['holdout']['precision'])}, recall {fmt(baseline['holdout']['recall'])}, F1 {fmt(baseline['holdout']['f1'])}, ROC-AUC {fmt(baseline['holdout']['roc_auc'])}, Brier {fmt(baseline['holdout']['brier_score'])}.",
        f"- Confusion matrix: `{baseline['holdout']['confusion_matrix']}`.",
        "",
        "## Controlled protocol",
        "",
        "1. The remote source was read without modification; the original data file was not written.",
        "2. A single stratified 80/20 split with seed 42 was created before candidate selection. The test partition was not used for tuning or selection.",
        "3. Candidate selection used only stratified five-fold cross-validation on the training partition, ranking ROC-AUC first and F1 second.",
        "4. Every imputer and scaler was inside the candidate pipeline and fit only on each training fold.",
        f"5. Robustness used independent stratified 80/20 splits with seeds {', '.join(map(str, SEEDS))}; it was not used to tune hyperparameters.",
        "6. No SMOTE or other resampling was used.",
        "",
        "## Candidate results",
        "",
        "All candidates were evaluated. Holdout values are descriptive only; candidate selection was based on training CV.",
        "",
        "| Candidate | CV accuracy | CV F1 | CV ROC-AUC | Test accuracy | Test F1 | Test ROC-AUC | Test Brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in ranked:
        cv = row["cv"]["mean"]
        holdout = row["holdout"]
        lines.append(f"| `{row['candidate_id']}` | {fmt(cv['accuracy'])} +/- {fmt(row['cv']['std']['accuracy'])} | {fmt(cv['f1'])} +/- {fmt(row['cv']['std']['f1'])} | {fmt(cv['roc_auc'])} +/- {fmt(row['cv']['std']['roc_auc'])} | {fmt(holdout['accuracy'])} | {fmt(holdout['f1'])} | {fmt(holdout['roc_auc'])} | {fmt(holdout['brier_score'])} |")
    lines.extend([
        "",
        "## Zero-policy comparison",
        "",
        "The comparison below keeps the feature set/model family selection visible rather than choosing a zero policy from holdout performance. `zero_as_missing` follows the documented clinical plausibility policy; `raw_zeros` preserves the source encoding.",
        "",
        "| Feature set | Model | Missing median CV ROC-AUC | Missing mean CV ROC-AUC | Raw zeros CV ROC-AUC |",
        "|---|---|---:|---:|---:|",
    ])
    for feature_set, feature_label in [("current_5", "Current 5"), ("all_8", "All 8")]:
        for model_name in ["logistic_regression", "random_forest", "gradient_boosting"]:
            variants = [r for r in ranked if r["feature_set"] == feature_set and r["model_name"] == model_name]
            def best_policy(policy: str, imputation: str | None = None):
                selected = [r for r in variants if r["zero_policy"] == policy and (imputation is None or r["imputation"] == imputation)]
                return max(selected, key=lambda r: r["cv"]["mean"]["roc_auc"]) if selected else None
            median = best_policy("zero_as_missing", "median")
            mean = best_policy("zero_as_missing", "mean")
            raw = best_policy("raw_zeros")
            lines.append(f"| {feature_label} | {model_name} | {fmt(median['cv']['mean']['roc_auc']) if median else 'n/a'} | {fmt(mean['cv']['mean']['roc_auc']) if mean else 'n/a'} | {fmt(raw['cv']['mean']['roc_auc']) if raw else 'n/a'} |")
    lines.extend(["", "## Scaling comparison", "", "Scaling is tested explicitly for Logistic Regression while keeping the feature set, zero policy, imputation, class weight, and C value matched. Tree models are reported without scaling because their split thresholds are invariant to monotonic numeric rescaling.", "", "| Feature set | Zero policy | Imputation | C | Scaled CV ROC-AUC | Unscaled CV ROC-AUC |", "|---|---|---|---:|---:|---:|"])
    for feature_set, feature_label in [("current_5", "Current 5"), ("all_8", "All 8")]:
        for zero_policy, imputation in [("zero_as_missing", "median"), ("zero_as_missing", "mean"), ("raw_zeros", "median")]:
            for c_value in (0.1, 1.0):
                c_suffix = "c0_1" if c_value == 0.1 else "c1"
                matching = [r for r in ranked if r["feature_set"] == feature_set and r["zero_policy"] == zero_policy and r["imputation"] == imputation and r["model_name"] == "logistic_regression" and r["cv"]["mean"].get("roc_auc") is not None and r["candidate_id"].endswith(c_suffix)]
                scaled = next((r for r in matching if r["candidate_id"].find("unscaled") == -1), None)
                unscaled = next((r for r in ranked if r["feature_set"] == feature_set and r["zero_policy"] == zero_policy and r["imputation"] == imputation and r["model_name"] == "logistic_regression" and r["candidate_id"].endswith(f"{c_suffix}__unscaled")), None)
                if scaled and unscaled:
                    lines.append(f"| {feature_label} | {zero_policy} | {imputation} | {c_value} | {fmt(scaled['cv']['mean']['roc_auc'])} | {fmt(unscaled['cv']['mean']['roc_auc'])} |")
    lines.extend(["", "## Best candidate details", "", f"```json\n{json.dumps(best_candidate, indent=2)}\n```", "", "### Best candidate confusion matrix", "", f"`{best['holdout']['confusion_matrix']}`", "", "## Five-seed robustness", "", "| Candidate | Mean accuracy +/- std | Mean precision +/- std | Mean recall +/- std | Mean F1 +/- std | Mean ROC-AUC +/- std |", "|---|---:|---:|---:|---:|---:|"])
    for candidate_id in [baseline["candidate_id"], best["candidate_id"]]:
        robust = result["robustness"][candidate_id]
        lines.append(f"| `{candidate_id}` | {fmt(robust['mean']['accuracy'])} +/- {fmt(robust['std']['accuracy'])} | {fmt(robust['mean']['precision'])} +/- {fmt(robust['std']['precision'])} | {fmt(robust['mean']['recall'])} +/- {fmt(robust['std']['recall'])} | {fmt(robust['mean']['f1'])} +/- {fmt(robust['std']['f1'])} | {fmt(robust['mean']['roc_auc'])} +/- {fmt(robust['std']['roc_auc'])} |")
    lines.extend(["", "Per-seed rows are included in the JSON result for reproducibility.", "", "## Limitations", "", "- One public dataset and no external validation cohort.", "- The remote dataset source is recorded, but full offline retraining requires obtaining that source separately.", "- The positive class is a minority (268/768); accuracy alone is insufficient, so precision, recall, F1, ROC-AUC, Brier score, and confusion matrices are reported.", "- Five-seed robustness reduces dependence on one split but does not replace external validation or confidence intervals.", "- Feature removal is not treated as an improvement claim; the all-feature configuration is the primary complete predictor comparison.", "- No production artifact, API, frontend, authentication, database schema, Heart Disease model, CKD model, or original dataset was changed.", "", "## Replacement decision", "", "`research_v1` remains the production artifact. A `research_v2` artifact should only be prepared after explicit approval and only if independent review accepts the training-CV and five-seed evidence above. This experiment does not claim approximately 85% accuracy unless the reported controlled results actually support that claim."])
    return "\n".join(lines) + "\n"


def main() -> None:
    raw_features, target, dataset_facts = load_raw_dataset()
    train_indices, test_indices = train_test_split(
        np.arange(len(raw_features)), test_size=TEST_SIZE, stratify=target, random_state=SELECTION_SEED
    )
    candidates = build_candidates()
    results: dict[str, Any] = {
        "experiment_id": "diabetes_model_improvement_v1",
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "protocol": {"selection_seed": SELECTION_SEED, "test_size": TEST_SIZE, "cv_splits": CV_SPLITS, "robustness_seeds": SEEDS, "test_isolated_before_selection": True, "smote_used": False},
        "dataset": dataset_facts,
        "baseline": {},
        "candidates": {},
        "candidate_ranking": [],
        "robustness": {},
    }
    for candidate in candidates:
        transformed = apply_zero_policy(raw_features[list(candidate.features)], candidate.zero_policy)
        train_features = transformed.iloc[train_indices]
        test_features = transformed.iloc[test_indices]
        train_target = target.iloc[train_indices]
        test_target = target.iloc[test_indices]
        cv = cross_validate_candidate(candidate, train_features, train_target)
        holdout = holdout_evaluate(candidate, train_features, train_target, test_features, test_target)
        results["candidates"][candidate.candidate_id] = {**candidate_to_dict(candidate), "cv": cv, "holdout": holdout}
    baseline_id = "current_5__zero_as_missing__median__logistic__balanced__c1"
    results["baseline"] = {"candidate_id": baseline_id, **results["candidates"][baseline_id]}
    ranking = []
    for candidate in candidates:
        row = results["candidates"][candidate.candidate_id]
        ranking.append({"candidate_id": candidate.candidate_id, "feature_set": candidate.feature_set, "zero_policy": candidate.zero_policy, "imputation": candidate.imputation, "model_name": candidate.model_name, "cv": row["cv"], "holdout": row["holdout"]})
    ranking.sort(key=lambda row: (row["cv"]["mean"]["roc_auc"], row["cv"]["mean"]["f1"]), reverse=True)
    results["candidate_ranking"] = ranking
    robustness_ids = {baseline_id, ranking[0]["candidate_id"]}
    for candidate_id in robustness_ids:
        candidate = next(item for item in candidates if item.candidate_id == candidate_id)
        transformed = apply_zero_policy(raw_features[list(candidate.features)], candidate.zero_policy)
        results["robustness"][candidate_id] = robustness(candidate, transformed, target)
    best_id = ranking[0]["candidate_id"]
    best_candidate = next(item for item in candidates if item.candidate_id == best_id)
    best_features = apply_zero_policy(raw_features[list(best_candidate.features)], best_candidate.zero_policy)
    candidate_model = make_candidate_pipeline(best_candidate, SELECTION_SEED)
    candidate_model.fit(best_features.iloc[train_indices], target.iloc[train_indices])
    artifact_dir = ROOT / "experiments" / "artifacts" / "diabetes_research_v2_candidate"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_metadata = {
        "disease_id": "diabetes",
        "model_version": "research_v2_candidate",
        "activation_status": "not_active",
        "candidate_id": best_id,
        "feature_names": list(best_candidate.features),
        "zero_policy": best_candidate.zero_policy,
        "imputation": best_candidate.imputation,
        "model_name": best_candidate.model_name,
        "class_weight": best_candidate.class_weight,
        "scale_numeric": best_candidate.scale_numeric,
        "hyperparameters": best_candidate.hyperparameters,
        "training_sample_count": int(len(train_indices)),
        "test_sample_count": int(len(test_indices)),
        "selection_protocol": results["protocol"],
        "cv_metrics": results["candidates"][best_id]["cv"],
        "held_out_metrics": results["candidates"][best_id]["holdout"],
        "robustness_metrics": results["robustness"][best_id],
        "source_dataset": DATA_URL,
        "note": "Candidate artifact prepared for review only. It is not loaded by the API and does not replace research_v1.",
    }
    joblib.dump({"pipeline": candidate_model, "metadata": artifact_metadata}, artifact_dir / "model_bundle.joblib")
    (artifact_dir / "metadata.json").write_text(json.dumps(artifact_metadata, indent=2), encoding="utf-8")
    results["candidate_artifact"] = {"path": str(artifact_dir.relative_to(ROOT)), **artifact_metadata}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"diabetes_model_improvement_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results, candidates), encoding="utf-8")
    print(f"Saved JSON results to {json_path}")
    print(f"Saved report to {REPORT_PATH}")
    print(f"Baseline: {baseline_id}")
    print(f"Best CV candidate: {ranking[0]['candidate_id']}")
    print("Best CV mean:", {metric: ranking[0]["cv"]["mean"][metric] for metric in METRICS})
    print("Best holdout:", {metric: ranking[0]["holdout"][metric] for metric in METRICS})
    print("Best robustness mean:", {metric: results["robustness"][ranking[0]["candidate_id"]]["mean"][metric] for metric in METRICS})


if __name__ == "__main__":
    main()
