from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Optional


class PredictionCreate(BaseModel):
    """Legacy diabetes request shape retained for API compatibility.

    Features used by the active saved research model:
    - age: Age in years
    - glucose: Fasting glucose in mg/dL
    - blood_pressure: Systolic blood pressure in mmHg
    - insulin: Fasting insulin in mU/ml
    - bmi: Body Mass Index in kg/m²
    
    Note: HbA1c is collected in profile but NOT used by the current diabetes model.
    """
    model_config = ConfigDict(allow_inf_nan=False)

    age: float = Field(gt=0, le=150)
    glucose: float = Field(ge=0)
    blood_pressure: float = Field(ge=0)
    insulin: float = Field(ge=0)
    bmi: float = Field(ge=0)


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    disease: str = "diabetes"
    glucose: float
    blood_pressure: float
    insulin: float
    bmi: float
    hba1c: Optional[float] = None  # Collected in profile but not used by model
    risk_percentage: float
    risk_level: str
    model_name: str = "research_model"
    model_version: str = "research_v1"
    created_at: datetime


class PredictionResponse(BaseModel):
    disease: str = "diabetes"
    risk_percentage: float
    risk_level: str
    probability: float
    model_name: str = "research_model"
    model_version: str = "research_v1"
    recommendations: List[str]
    created_at: datetime


class DiseasePredictionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    features: Dict[str, Any]


class DiseasePredictionResponse(BaseModel):
    disease: str
    display_name: str
    model_name: str
    model_version: str
    prediction_class: Any
    probabilities: Optional[Dict[str, float]] = None
    positive_class_probability: Optional[float] = None
    risk_level: Optional[str] = None
    feature_importance: List[Dict[str, Any]]
    input_data: Optional[Dict[str, Any]] = None
    research_disclaimer: str
    created_at: datetime


class ModelInfoResponse(BaseModel):
    disease_id: str
    display_name: str
    training_status: str
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    dataset_name: str
    dataset_source: str
    target: Optional[str] = None
    feature_names: List[str]
    numeric_features: List[str] = []
    categorical_features: List[str] = []
    task_type: Optional[str] = None
    training_date: Optional[str] = None
    evaluation_metrics: Optional[Dict[str, Any]] = None
    training_sample_count: Optional[int] = None
    test_sample_count: Optional[int] = None
    limitations: List[str]
    preprocessing: Optional[str] = None
    dataset_policy: Optional[str] = None
    dataset_sample_count: Optional[int] = None
    training_test_methodology: str = "Stratified 80/20 train/test split with random seed 42"
    cross_validation_methodology: str = "Stratified 5-fold cross-validation on the training partition"
