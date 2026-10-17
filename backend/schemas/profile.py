from pydantic import BaseModel, ConfigDict
from typing import Optional


class PatientProfileBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    smoking: Optional[str] = None
    alcohol: Optional[str] = None
    activity: Optional[str] = None
    family_history: Optional[str] = None


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileOut(PatientProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    bmi: Optional[float] = None
