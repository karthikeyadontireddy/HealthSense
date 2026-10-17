from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Optional

from backend.config import BASE_DIR

DISPLAY_MODEL_NAMES = {
    "diabetes": "Logistic Regression",
    "heart_disease": "Logistic Regression",
    "ckd": "Random Forest",
}


@dataclass(frozen=True)
class DiseaseModelConfig:
    disease_id: str
    display_name: str
    model_path: Path
    dataset_name: str
    dataset_source: str
    target: Optional[str]
    feature_names: tuple[str, ...]
    task_type: Optional[str]
    training_status: str
    numeric_features: tuple[str, ...] = ()
    categorical_features: tuple[str, ...] = ()
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    training_date: Optional[str] = None
    evaluation_metrics: Optional[dict[str, Any]] = None
    training_sample_count: Optional[int] = None
    test_sample_count: Optional[int] = None
    limitations: tuple[str, ...] = ()
    preprocessing: Optional[str] = None
    dataset_policy: Optional[str] = None
    metadata_path: Optional[Path] = None


def _artifact_config(disease_id: str, display_name: str, output_dir: Path, fallback: dict[str, Any]):
    metadata_path = output_dir / "metadata.json"
    artifact_path = output_dir / "model_bundle.joblib"
    if not metadata_path.exists() or not artifact_path.exists():
        return DiseaseModelConfig(
            disease_id=disease_id,
            display_name=display_name,
            model_path=artifact_path,
            dataset_name=fallback["dataset_name"],
            dataset_source=fallback["dataset_source"],
            target=fallback["target"],
            feature_names=tuple(fallback["feature_names"]),
            numeric_features=(),
            categorical_features=(),
            task_type=None,
            training_status="Dataset available - model not trained",
            metadata_path=metadata_path,
        )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return DiseaseModelConfig(
        disease_id=disease_id,
        display_name=display_name,
        model_path=artifact_path,
        dataset_name=metadata["dataset_name"],
        dataset_source=metadata["dataset_source"],
        target=metadata["target"],
        feature_names=tuple(metadata["feature_names"]),
        numeric_features=tuple(metadata.get("numeric_features", [])),
        categorical_features=tuple(metadata.get("categorical_features", [])),
        task_type=metadata["task_type"],
        training_status="trained artifact available",
        model_name=DISPLAY_MODEL_NAMES.get(disease_id, metadata["model_name"]),
        model_version=metadata["model_version"],
        training_date=metadata["training_date"],
        evaluation_metrics=metadata["evaluation_metrics"],
        training_sample_count=metadata["training_sample_count"],
        test_sample_count=metadata["test_sample_count"],
        limitations=tuple(metadata["limitations"]),
        preprocessing=metadata.get("preprocessing"),
        dataset_policy=metadata.get("dataset_policy"),
        metadata_path=metadata_path,
    )


def build_registry():
    return {
        "diabetes": _artifact_config(
            "diabetes", "Diabetes Risk", BASE_DIR / "ml" / "models" / "diabetes",
            {"dataset_name": "Plotly diabetes dataset", "dataset_source": "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv", "target": "Outcome", "feature_names": ["Glucose", "BloodPressure", "Insulin", "BMI", "Age"]},
        ),
        "heart_disease": _artifact_config(
            "heart_disease", "Heart Disease Risk", BASE_DIR / "ml" / "models" / "heart",
            {"dataset_name": "UCI Heart Disease Cleveland subset", "dataset_source": "backend/datasets/heart/original/processed.cleveland.data", "target": "num_binary", "feature_names": ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]},
        ),
        "ckd": _artifact_config(
            "ckd", "Chronic Kidney Disease Risk", BASE_DIR / "ml" / "models" / "ckd",
            {"dataset_name": "Early stage of Indians Chronic Kidney Disease", "dataset_source": "backend/datasets/ckd/original/chronic_kidney_disease.arff", "target": "class_binary", "feature_names": []},
        ),
    }


MODEL_REGISTRY = build_registry()


def get_model_config(disease_id: str) -> DiseaseModelConfig:
    try:
        return MODEL_REGISTRY[disease_id]
    except KeyError as error:
        raise ValueError(f"Unknown disease: {disease_id}") from error
