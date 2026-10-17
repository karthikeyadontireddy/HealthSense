from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, get_db
from backend.ml.model_registry import DISPLAY_MODEL_NAMES
from backend.models.prediction import Prediction
from backend.schemas.prediction import PredictionOut

router = APIRouter()


@router.get("/history", response_model=list[PredictionOut])
def get_history(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return [
        PredictionOut.model_validate(prediction).model_copy(
            update={"model_name": DISPLAY_MODEL_NAMES.get(prediction.disease, prediction.model_name)}
        )
        for prediction in predictions
    ]
