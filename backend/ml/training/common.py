from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_SPLITS = 5


def make_preprocessor(numeric_features: list[str], categorical_features: list[str], scale_numeric: bool):
    numeric_steps = [
        ("imputer", SimpleImputer(strategy="median")),
    ]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    transformers = [("numeric", Pipeline(numeric_steps), numeric_features)]
    if categorical_features:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_features,
            )
        )
    return ColumnTransformer(transformers=transformers, remainder="drop")


def candidate_models(random_state: int = RANDOM_STATE):
    return {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=random_state),
    }


def make_pipeline(model_name: str, model, numeric_features: list[str], categorical_features: list[str]):
    return Pipeline(
        [
            (
                "preprocess",
                make_preprocessor(
                    numeric_features,
                    categorical_features,
                    scale_numeric=model_name == "logistic_regression",
                ),
            ),
            ("model", model),
        ]
    )


def _positive_scores(model, features):
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)
        if probabilities.shape[1] == 2:
            return probabilities[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(features)
    return None


def evaluate(model, features, target) -> dict[str, Any]:
    predictions = model.predict(features)
    scores = _positive_scores(model, features)
    metrics = {
        "accuracy": float(accuracy_score(target, predictions)),
        "precision": float(precision_score(target, predictions, zero_division=0)),
        "recall": float(recall_score(target, predictions, zero_division=0)),
        "f1": float(f1_score(target, predictions, zero_division=0)),
        "confusion_matrix": confusion_matrix(target, predictions).tolist(),
    }
    if scores is not None and len(np.unique(target)) == 2:
        metrics["roc_auc"] = float(roc_auc_score(target, scores))
    else:
        metrics["roc_auc"] = None
    return metrics


def feature_importance(model) -> list[dict[str, Any]]:
    preprocessor = model.named_steps["preprocess"]
    estimator = model.named_steps["model"]
    names = list(preprocessor.get_feature_names_out())
    if hasattr(estimator, "feature_importances_"):
        values = np.asarray(estimator.feature_importances_, dtype=float)
        method = "feature_importances_"
    elif hasattr(estimator, "coef_"):
        values = np.abs(np.asarray(estimator.coef_[0], dtype=float))
        method = "absolute_coefficients"
    else:
        return []
    order = np.argsort(values)[::-1]
    return [
        {"feature": names[index], "importance": float(values[index]), "method": method}
        for index in order[:20]
    ]


def train_and_save(
    *,
    disease_id: str,
    display_name: str,
    dataset_name: str,
    dataset_source: str,
    target_name: str,
    feature_names: list[str],
    numeric_features: list[str],
    categorical_features: list[str],
    features,
    target,
    output_dir: Path,
    model_version: str,
    preprocessing_description: str,
    dataset_policy: str,
    limitations: list[str],
    dropped_rows: list[dict[str, Any]] | None = None,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        stratify=target,
        random_state=RANDOM_STATE,
    )
    cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    scoring = {"accuracy": "accuracy", "precision": "precision", "recall": "recall", "f1": "f1", "roc_auc": "roc_auc"}
    comparisons = []
    for model_name, estimator in candidate_models().items():
        pipeline = make_pipeline(model_name, estimator, numeric_features, categorical_features)
        scores = cross_validate(pipeline, x_train, y_train, cv=cv, scoring=scoring, n_jobs=1, error_score="raise")
        comparisons.append(
            {
                "model_name": model_name,
                "cv_mean": {metric: float(np.mean(scores[f"test_{metric}"])) for metric in scoring},
                "cv_std": {metric: float(np.std(scores[f"test_{metric}"])) for metric in scoring},
            }
        )
    selected = max(comparisons, key=lambda item: (item["cv_mean"]["roc_auc"], item["cv_mean"]["f1"]))
    selected_name = selected["model_name"]
    final_model = make_pipeline(selected_name, candidate_models()[selected_name], numeric_features, categorical_features)
    final_model.fit(x_train, y_train)
    test_metrics = evaluate(final_model, x_test, y_test)
    metadata = {
        "disease_id": disease_id,
        "display_name": display_name,
        "dataset_name": dataset_name,
        "dataset_source": dataset_source,
        "target": target_name,
        "feature_names": feature_names,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "task_type": "binary classification",
        "preprocessing": preprocessing_description,
        "dataset_policy": dataset_policy,
        "model_name": selected_name,
        "model_version": model_version,
        "training_date": datetime.now(timezone.utc).isoformat(),
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "cv_splits": CV_SPLITS,
        "training_sample_count": int(len(x_train)),
        "test_sample_count": int(len(x_test)),
        "dataset_sample_count_after_policy": int(len(features)),
        "dropped_rows": dropped_rows or [],
        "model_comparison": comparisons,
        "evaluation_metrics": test_metrics,
        "feature_importance": feature_importance(final_model),
        "limitations": limitations,
    }
    joblib.dump({"pipeline": final_model, "metadata": metadata}, output_dir / "model_bundle.joblib")
    (output_dir / "metadata.json").write_text(__import__("json").dumps(metadata, indent=2), encoding="utf-8")
    (output_dir / "model_comparison.json").write_text(__import__("json").dumps(comparisons, indent=2), encoding="utf-8")
    print(f"{display_name}: selected {selected_name}")
    print(f"  training samples: {len(x_train)}, test samples: {len(x_test)}")
    for metric, value in test_metrics.items():
        print(f"  {metric}: {value}")
    return metadata
