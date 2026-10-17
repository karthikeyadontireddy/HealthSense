import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, get_db
from backend.ml.model_registry import DISPLAY_MODEL_NAMES, MODEL_REGISTRY
from backend.models.prediction import Prediction
from backend.schemas.prediction import (
    DiseasePredictionCreate,
    DiseasePredictionResponse,
    ModelInfoResponse,
    PredictionCreate,
    PredictionResponse,
)
from backend.services.multi_prediction import predict as predict_model

router = APIRouter()


@router.get("/research/metrics")
def research_metrics(current_user=Depends(get_current_user)):
    """Return the latest scientific validation artifact for research reporting."""
    validation_path = Path(__file__).resolve().parent.parent / "ml" / "validation" / "validation_results.json"
    if not validation_path.exists():
        raise HTTPException(status_code=404, detail="Scientific validation results are not available yet.")
    try:
        artifact = json.loads(validation_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=503, detail="Scientific validation results are invalid.") from error
    for disease_id, model_name in DISPLAY_MODEL_NAMES.items():
        if disease_id in artifact.get("diseases", {}):
            artifact["diseases"][disease_id]["model_name"] = model_name
    return {
        "source_file": str(validation_path.relative_to(Path(__file__).resolve().parent.parent)),
        "loaded_at": datetime.now(timezone.utc).isoformat(),
        "artifact": artifact,
        "models": {
            disease_id: {
                "display_name": config.display_name,
                "model_name": config.model_name,
                "model_version": config.model_version,
                "dataset_name": config.dataset_name,
                "dataset_source": config.dataset_source,
                "target": config.target,
                "task_type": config.task_type,
                "feature_names": list(config.feature_names),
                "numeric_features": list(config.numeric_features),
                "categorical_features": list(config.categorical_features),
                "preprocessing": config.preprocessing,
                "dataset_policy": config.dataset_policy,
                "training_date": config.training_date,
                "training_sample_count": config.training_sample_count,
                "test_sample_count": config.test_sample_count,
                "evaluation_metrics": config.evaluation_metrics,
                "limitations": list(config.limitations),
            }
            for disease_id, config in MODEL_REGISTRY.items()
        },
    }


def _store_prediction(db: Session, user_id: int, result: dict, features: dict):
    legacy = {name: float(features.get(name, 0)) for name in ("glucose", "blood_pressure", "insulin", "bmi")}
    positive_probability = result.get("positive_class_probability")
    risk_percentage = round(positive_probability * 100, 1) if positive_probability is not None else 0.0
    risk_level = result.get("risk_level") or f"Model class: {result['prediction_class']}"
    prediction = Prediction(
        user_id=user_id,
        disease=result["disease"],
        glucose=legacy["glucose"],
        blood_pressure=legacy["blood_pressure"],
        insulin=legacy["insulin"],
        bmi=legacy["bmi"],
        hba1c=None,
        risk_percentage=risk_percentage,
        risk_level=risk_level,
        model_name=result["model_name"],
        model_version=result["model_version"],
        input_data=features,
    )
    db.add(prediction)
    db.commit()
    return prediction


@router.post("/predict/{disease}", response_model=DiseasePredictionResponse)
def predict_disease(
    disease: str,
    data: DiseasePredictionCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if disease not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="Unknown disease model.")
    try:
        result = predict_model(disease, data.features)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="This disease model has not been trained yet.")
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))
    _store_prediction(db, current_user.id, result, data.features)
    return result


@router.get("/models", response_model=list[ModelInfoResponse])
def list_models(current_user=Depends(get_current_user)):
    return [
        {
            "disease_id": config.disease_id,
            "display_name": config.display_name,
            "training_status": config.training_status,
            "model_name": config.model_name,
            "model_version": config.model_version,
            "dataset_name": config.dataset_name,
            "dataset_source": config.dataset_source,
            "target": config.target,
            "feature_names": list(config.feature_names),
            "numeric_features": list(config.numeric_features),
            "categorical_features": list(config.categorical_features),
            "task_type": config.task_type,
            "training_date": config.training_date,
            "evaluation_metrics": config.evaluation_metrics,
            "training_sample_count": config.training_sample_count,
            "test_sample_count": config.test_sample_count,
            "limitations": list(config.limitations),
            "preprocessing": config.preprocessing,
            "dataset_policy": config.dataset_policy,
            "dataset_sample_count": config.training_sample_count + config.test_sample_count if config.training_sample_count is not None and config.test_sample_count is not None else None,
            "training_test_methodology": "Stratified 80/20 train/test split with random seed 42",
            "cross_validation_methodology": "Stratified 5-fold cross-validation on the training partition",
        }
        for config in MODEL_REGISTRY.values()
    ]


@router.post("/predict", response_model=PredictionResponse)
def predict_legacy(data: PredictionCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        result = predict_model(
            "diabetes",
            {
                "Glucose": data.glucose,
                "BloodPressure": data.blood_pressure,
                "Insulin": data.insulin,
                "BMI": data.bmi,
                "Age": data.age,
            },
        )
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail=str(error))
    prediction = _store_prediction(
        db,
        current_user.id,
        result,
        {"Glucose": data.glucose, "BloodPressure": data.blood_pressure, "Insulin": data.insulin, "BMI": data.bmi, "Age": data.age},
    )
    return {
        "disease": "diabetes",
        "risk_percentage": round(result["positive_class_probability"] * 100, 1),
        "risk_level": result["risk_level"],
        "probability": round(result["positive_class_probability"], 6),
        "model_name": result["model_name"],
        "model_version": result["model_version"],
        "recommendations": [
            "This is a model-estimated probability for research and educational use.",
            "Consider discussing relevant measurements with a qualified healthcare professional.",
        ],
        "created_at": prediction.created_at,
    }
