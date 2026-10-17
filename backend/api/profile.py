from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, get_db
from backend.models.profile import PatientProfile
from backend.schemas.profile import PatientProfileCreate, PatientProfileOut

router = APIRouter()


@router.get("/profile", response_model=PatientProfileOut)
def get_profile(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        profile = PatientProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/profile", response_model=PatientProfileOut)
def update_profile(profile_in: PatientProfileCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    bmi = None
    if profile_in.height and profile_in.weight:
        bmi = round(profile_in.weight / ((profile_in.height / 100) ** 2), 1)
    if not profile:
        profile = PatientProfile(user_id=current_user.id, bmi=bmi, **profile_in.dict())
        db.add(profile)
    else:
        for field, value in profile_in.dict().items():
            setattr(profile, field, value)
        profile.bmi = bmi
    db.commit()
    db.refresh(profile)
    return profile
